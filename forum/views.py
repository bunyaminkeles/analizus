from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse
from django import forms
from django.conf import settings
import json
from django.contrib.auth import login
import re
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef
from django.contrib import messages
from django.utils import timezone
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import timedelta
import uuid
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import Section, Category, Topic, Post, Profile, PrivateMessage, PostLike, Notification, EmailVerification, DailyTip, QuizQuestion, QuizScore, SuccessStory, FreelanceJob, JobCategory, JobProposal, JobReview, Skill, Badge, UserQuizAttempt, JobPayment, SiteSettings, BlogCategory, BlogPost, BlogTag, DonationTier, StudyRoom, StudyRoomMembership, StudyRoomPost, STUDYROOM_TERMS, ReferralCode, ReferralUse
from .forms import RegisterForm, NewTopicForm, PostForm, JobPostForm, ProposalForm
from .email_utils import send_topic_reply_notification, send_private_message_notification
from django.template.loader import render_to_string
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def feature_required(flag_name):
    """Decorator: SiteSettings'deki feature flag kapalıysa 404 döner."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            site = SiteSettings.load()
            if not getattr(site, f'feature_{flag_name}', True):
                from django.http import Http404
                raise Http404
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# --- HEALTH CHECK (Cron ping için) ---
@require_GET
def health_check(request):
    """Basit health check endpoint - cron job ping için"""
    return JsonResponse({'status': 'ok'}, status=200)



# --- RATE LIMIT HATA SAYFASI ---
def ratelimit_error(request, exception):
    """Rate limit aşıldığında gösterilecek hata sayfası"""
    return render(request, 'forum/ratelimit_error.html', status=429)


# --- FORUM BÖLÜMLER ---
def forum_index(request):
    from django.db.models import Max, OuterRef, Subquery
    from .models import Post

    # Her kategori için konu sayısı, toplam gönderi sayısı, son gönderi zamanı
    last_post_time = Post.objects.filter(
        topic__category=OuterRef('pk')
    ).order_by('-created_at').values('created_at')[:1]

    categories_qs = Category.objects.annotate(
        topic_count=Count('topics', distinct=True),
        post_count=Count('topics__posts', distinct=True),
        last_post_at=Subquery(last_post_time),
    ).select_related('section')

    # En aktif 5 kategoriyi popüler say
    top_slugs = set(
        categories_qs.order_by('-topic_count').values_list('slug', flat=True)[:5]
    )

    # Section'lara kategorileri bağla
    now = timezone.now()
    cutoff = now - timedelta(days=30)
    sections = Section.objects.all().order_by('order')
    from datetime import datetime as _dt, timezone as _pytz
    _epoch = _dt(1970, 1, 1, tzinfo=_pytz.utc)
    sections_data = []
    for section in sections:
        cats = [c for c in categories_qs if c.section_id == section.pk]
        for c in cats:
            c.is_popular = c.slug in top_slugs
            c.show_last_activity = (
                c.last_post_at is not None and c.last_post_at >= cutoff
            )
        # Son aktivitesi olanlar önce, hiç konu olmayanlar sona
        cats.sort(key=lambda c: c.last_post_at or _epoch, reverse=True)
        sections_data.append({'section': section, 'categories': cats})

    # Aktif çalışma odaları (en fazla 6)
    active_rooms = (
        StudyRoom.objects
        .filter(status='active')
        .select_related('category', 'creator')
        .annotate(member_cnt=Count('memberships', distinct=True))
        .order_by('-created_at')[:6]
    )
    # Süresi dolanları sessizce arşivle
    for room in StudyRoom.objects.filter(status='active'):
        room.auto_archive_if_expired()

    from forum.models import STUDYROOM_TERMS
    can_create_room, _ = _studyroom_eligibility(request.user)

    return render(request, 'forum/forum_index.html', {
        'sections_data': sections_data,
        'active_rooms': active_rooms,
        'can_create_room': can_create_room,
    })


def _get_featured_experts():
    """Uzman Vitrini — /uzmanlar/ (uzman_dizini) varsayılan "puan" sıralamasıyla
    birebir aynı kriter + sıra. 5 dk cache (home_experts). Ana sayfa ve /market/
    arasında paylaşılır — tekrar hesaplama yapılmaz."""
    from django.core.cache import cache

    featured_experts = cache.get('home_experts')
    if featured_experts is None:
        featured_experts = list(
            Profile.objects
            .select_related('user')
            .prefetch_related('skills')
            .filter(is_public=True)
            .filter(
                Q(rank__in=['contributor', 'expert', 'master', 'legend', 'admin'])
                | Q(skills__isnull=False)
                | Q(best_answers_count__gt=0)
            )
            .exclude(user__username='admin')
            .distinct()
            .annotate(
                showcase_completed_jobs=Count(
                    'user__proposals',
                    filter=Q(user__proposals__status='accepted', user__proposals__job__status='completed'),
                    distinct=True,
                ),
                avg_rating=Avg(
                    'user__received_reviews__rating',
                    filter=Q(user__received_reviews__is_approved=True),
                ),
            )
            .order_by('-reputation', '-showcase_completed_jobs')[:4]
        )
        cache.set('home_experts', featured_experts, 300)
    return featured_experts


# --- ANA SAYFA ---
@ensure_csrf_cookie
def home(request):
    sections = Section.objects.all().order_by('order')

    # Widget verileri
    # İstatistikler — 5 dk cache (home_stats): her istekte 8 ayrı sorgu yerine cache hit'te 0 sorgu
    from django.core.cache import cache
    from istatistik.models import IstatistikJob

    home_stats = cache.get('home_stats')
    if home_stats is None:
        online_cutoff = timezone.now() - timedelta(minutes=5)
        home_stats = {
            'total_topics': Topic.objects.count(),
            'total_posts': Post.objects.count(),
            'total_users': User.objects.count(),
            'completed_jobs': FreelanceJob.objects.filter(status='completed').count(),
            'weekly_new_users': User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count(),
            'open_jobs_count': FreelanceJob.objects.filter(status='open').count(),
            'active_experts_count': User.objects.filter(proposals__job__status='completed').distinct().count(),
            # Tamamlanan Analiz — IstatistikJob bazlı; "Tamamlanan Proje" (FreelanceJob) ile karıştırılmasın
            'completed_analyses': IstatistikJob.objects.filter(status='completed').count(),
            # Şu an çevrimiçi uzman — Profile.is_online bir Python property, ORM'de kullanılamaz;
            # last_seen üzerinden DB seviyesinde filtrelenir
            'online_experts': Profile.objects.filter(
                Q(rank__in=['expert', 'master', 'legend', 'admin']) | Q(account_type='Expert'),
                last_seen__gte=online_cutoff,
            ).count(),
        }
        cache.set('home_stats', home_stats, 300)

    total_topics = home_stats['total_topics']
    total_posts = home_stats['total_posts']
    total_users = home_stats['total_users']
    completed_jobs = home_stats['completed_jobs']
    weekly_new_users = home_stats['weekly_new_users']
    open_jobs_count = home_stats['open_jobs_count']
    active_experts_count = home_stats['active_experts_count']
    completed_analyses = home_stats['completed_analyses']
    online_experts = home_stats['online_experts']

    featured_experts = _get_featured_experts()

    # Son değerlendirmeler (sosyal kanıt)
    recent_reviews = JobReview.objects.filter(is_approved=True).select_related('reviewer', 'reviewed_user', 'job').order_by('-created_at')[:5]

    # Son tartışmalar (son 5 aktif konu)
    recent_topics = Topic.objects.select_related('starter', 'category').annotate(
        replies_count=Count('posts')
    ).order_by('-created_at')[:5]

    # Popüler konular (en çok görüntülenen 5 konu)
    popular_topics = Topic.objects.select_related('starter', 'category').annotate(
        replies_count=Count('posts')
    ).order_by('-views')[:5]

    # Günün İpucu
    daily_tip = DailyTip.get_today_tip()

    # Quiz Sorusu
    quiz_question = QuizQuestion.get_random_question()

    # Haftanın Başarı Hikayesi
    featured_story = SuccessStory.objects.filter(is_featured=True, approval_status='approved').first()
    if not featured_story:
        featured_story = SuccessStory.objects.filter(approval_status='approved').order_by('?').first()

    # Ana sayfa blog kartları (son 3 yayınlanmış)
    latest_posts = BlogPost.objects.filter(status='published').select_related('author', 'category').order_by('-published_at')[:3]

    # Carousel için onaylı hikayeler (max 6)
    success_stories = list(
        SuccessStory.objects.filter(approval_status='approved')
        .select_related('user', 'user__profile')
        .order_by('-is_featured', '-created_at')[:6]
    )

    # Freelance Market - Son İlanlar
    recent_jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category').annotate(
        p_count=Count('proposals', distinct=True)
    ).order_by('-created_at')[:5]

    # Vitrin İlanları (Öne Çıkanlar) - Süresi dolmamış olanlar
    featured_jobs = FreelanceJob.objects.filter(
        status='open',
        is_featured=True,
        featured_until__gte=timezone.now()  # Vitrin süresi dolmamış
    ).select_related('owner', 'category').annotate(
        p_count=Count('proposals', distinct=True)
    ).order_by('-created_at')[:4]

    # Bağış Katmanları
    donation_tiers = DonationTier.objects.filter(is_active=True).order_by('min_amount')

    # Güncel Haberler
    from .news_utils import get_science_news
    science_news = get_science_news()

    context = {
        'sections': sections,
        # İstatistikler
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
        'completed_jobs': completed_jobs,
        'weekly_new_users': weekly_new_users,
        'open_jobs_count': open_jobs_count,
        'active_experts_count': active_experts_count,
        'completed_analyses': completed_analyses,
        'online_experts': online_experts,
        'featured_experts': featured_experts,
        # Widgetlar
        'recent_topics': recent_topics,
        'popular_topics': popular_topics,
        'daily_tip': daily_tip,
        'quiz_question': quiz_question,
        'donation_tiers': donation_tiers,
        'featured_story': featured_story,
        'success_stories': success_stories,
        'latest_posts': latest_posts,
        'recent_jobs': recent_jobs,
        'recent_reviews': recent_reviews,
        'featured_jobs': featured_jobs,
        'science_news': science_news,
    }
    return render(request, 'forum/home.html', context)

# --- BAŞARI HİKAYELERİ ---
class SuccessStoryForm(forms.ModelForm):
    achievements_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örnek:\n- Tezi 3 ayda bitirdim\n- Analiz korkumu yendim'}), 
        help_text="Her satıra bir başarı maddesi yazınız.", 
        required=False, 
        label="Başarılar (Her satıra bir tane)"
    )
    resources_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örnek:\n- Analizus Forum\n- YouTube SPSS Serisi'}), 
        help_text="Kullandığınız kaynakları alt alta yazınız.", 
        required=False, 
        label="Kaynaklar"
    )

    class Meta:
        model = SuccessStory
        fields = ['quote']
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Hikayenizi kısaca anlatın...'}),
        }
        labels = {'quote': 'Hikayeniz'}

@feature_required('success_stories')
def success_stories(request):
    stories = SuccessStory.objects.filter(approval_status='approved').order_by('-is_featured', '-created_at')
    form = None
    job = None
    auto_open_modal = False

    # ?job=<pk> parametresi ile geldiyse ilgili ilanı bul
    job_id = request.GET.get('job')
    if job_id:
        job = FreelanceJob.objects.filter(pk=job_id, status='completed').first()
        if job and request.user.is_authenticated:
            auto_open_modal = True

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SuccessStoryForm(request.POST)
            if form.is_valid():
                story = form.save(commit=False)
                story.user = request.user
                # Text alanlarını listeye çevir
                story.achievements = [line.strip() for line in form.cleaned_data['achievements_text'].split('\n') if line.strip()]
                story.resources = [line.strip() for line in form.cleaned_data['resources_text'].split('\n') if line.strip()]

                # Job bağlantısı
                post_job_id = request.POST.get('job_id')
                if post_job_id:
                    linked_job = FreelanceJob.objects.filter(pk=post_job_id, status='completed').first()
                    if linked_job:
                        # Kullanıcı ilan sahibi mi, yoksa kabul edilen uzman mı?
                        is_owner = linked_job.owner == request.user
                        is_expert = linked_job.proposals.filter(expert=request.user, status='accepted').exists()
                        if is_owner or is_expert:
                            story.job = linked_job

                story.approval_status = 'pending'
                story.save()
                messages.success(request, 'Hikayeniz gönderildi! Admin onayından sonra yayınlanacaktır.')
                return redirect('success_stories')
        else:
            form = SuccessStoryForm()

    return render(request, 'forum/success_stories.html', {
        'stories': stories,
        'form': form,
        'linked_job': job,
        'auto_open_modal': auto_open_modal,
    })

# --- FREELANCE MARKET ---
@feature_required('market')
def job_list(request):
    from django.utils import timezone as tz
    from datetime import timedelta
    now = tz.now()
    three_months_ago = now - timedelta(days=90)

    # Süresi dolan açık ilanları otomatik kapat; bekleyen teklifleri de reddet
    expired_qs = FreelanceJob.objects.filter(status='open', expires_at__lt=now)
    JobProposal.objects.filter(job__in=expired_qs, status='pending').update(status='rejected')
    expired_qs.update(status='cancelled')

    old_qs = FreelanceJob.objects.filter(status='open', expires_at__isnull=True, created_at__lt=now - timedelta(days=30))
    JobProposal.objects.filter(job__in=old_qs, status='pending').update(status='rejected')
    old_qs.update(status='cancelled')

    sort = request.GET.get('sort', 'newest')
    jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category').annotate(
        p_count=Count('proposals', distinct=True)
    )

    # Kategori Gezinmesi — chip listesi, filtre uygulanmadan önceki açık ilanlardan
    # çıkarılır (seçili kategori değişince chip'ler daralmasın)
    market_categories = JobCategory.objects.filter(jobs__status='open').distinct().order_by('order', 'title')
    selected_category = None
    category_id = request.GET.get('category')
    if category_id and category_id.isdigit():
        selected_category = int(category_id)
        jobs = jobs.filter(category_id=selected_category)

    if sort == 'views':
        jobs = jobs.order_by('-views', '-created_at')
    elif sort == 'proposals':
        jobs = jobs.order_by('-p_count', '-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    # İstatistikler
    completed_qs = FreelanceJob.objects.filter(status='completed')
    recent_completed_qs = completed_qs.filter(updated_at__gte=three_months_ago)
    avg_budget = completed_qs.aggregate(avg=Avg('budget_max'))['avg'] or 0
    total_experts = JobProposal.objects.values('expert').distinct().count()

    market_stats = {
        'total_completed': completed_qs.count(),
        'recent_completed': recent_completed_qs.count(),
        'avg_budget': int(avg_budget),
        'total_experts': total_experts,
        'open_count': jobs.count(),
    }

    # Son 3 ayda tamamlanan ilanlar (max 6, en yeni önce)
    completed_jobs = (
        recent_completed_qs
        .select_related('category')
        .annotate(p_count=Count('proposals', distinct=True))
        .order_by('-updated_at')[:6]
    )

    # Yetki bilgileri
    can_post = FreelanceJob.can_post(request.user)
    can_post_reason = ""
    can_propose = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        _, can_post_reason = request.user.profile.can_post_job()
        can_propose, _ = request.user.profile.can_propose()

    # Uzman Vitrini — ana sayfayla aynı sorgu/cache (home_experts)
    featured_experts = _get_featured_experts()

    # Başarı Hikayesi şeridi (varsa)
    success_stories = list(
        SuccessStory.objects.filter(approval_status='approved')
        .select_related('user', 'user__profile')
        .order_by('-is_featured', '-created_at')[:3]
    )

    return render(request, 'forum/market/job_list.html', {
        'jobs': jobs,
        'current_sort': sort,
        'can_post': can_post,
        'can_post_reason': can_post_reason,
        'can_propose': can_propose,
        'market_stats': market_stats,
        'completed_jobs': completed_jobs,
        'market_categories': market_categories,
        'selected_category': selected_category,
        'featured_experts': featured_experts,
        'success_stories': success_stories,
    })

@feature_required('market')
@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=True)
def post_job(request):
    from datetime import timedelta
    from django.utils import timezone

    profile = request.user.profile
    can_post, reason = profile.can_post_job_now()
    if not can_post:
        messages.error(request, reason)
        return redirect('job_list')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.expires_at = timezone.now() + timedelta(days=profile.get_job_duration_days())
            if profile.is_first_job():
                job.is_featured = True
                job.featured_until = timezone.now() + timedelta(days=3)  # 3 gün hediye
                messages.info(request, 'İlk ilanınız olduğu için 3 gün öne çıkarma hediyesi kazandınız!')
            job.save()
            messages.success(request, f'İş ilanı başarıyla oluşturuldu. ({profile.get_job_duration_days()} gün aktif kalacak)')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobPostForm()
    from .models import JobCategory
    job_categories = JobCategory.objects.filter(is_active=True).values_list('title', flat=True)
    return render(request, 'forum/market/post_job.html', {
        'form': form,
        'job_categories': job_categories,
        'job_duration_days': profile.get_job_duration_days(),
    })

@login_required
def toggle_job_like(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)
    if request.user in job.likes.all():
        job.likes.remove(request.user)
        messages.info(request, "Beğeni geri alındı.")
    else:
        job.likes.add(request.user)
        messages.success(request, "İlan beğenildi!")
    return redirect('job_detail', pk=pk)

@login_required
def toggle_job_bookmark(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)
    if request.user in job.saved_by.all():
        job.saved_by.remove(request.user)
        messages.info(request, "İlan kaydedilenlerden çıkarıldı.")
    else:
        job.saved_by.add(request.user)
        messages.success(request, "İlan kaydedildi!")
    return redirect('job_detail', pk=pk)

@login_required
@require_POST
def close_job(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)

    if job.status == 'open':
        # Bekleyen teklif sahiplerine DM gönder
        pending_proposals = job.proposals.filter(status='pending').select_related('expert')
        try:
            bot_user = User.objects.get(username='AnalizBot')
        except User.DoesNotExist:
            bot_user = request.user

        for proposal in pending_proposals:
            PrivateMessage.objects.create(
                sender=bot_user,
                receiver=proposal.expert,
                message=(
                    f'Merhaba {proposal.expert.username},\n\n'
                    f'Teklif verdiğiniz "{job.title}" ilanı ilan sahibi tarafından yayından kaldırıldı. '
                    f'Teklifiniz otomatik olarak iptal edilmiştir.\n\n'
                    f'Diğer ilanları incelemek için: {getattr(settings, "SITE_URL", "https://www.analizus.com")}/market/'
                )
            )

        job.status = 'cancelled'
        job.save()
        messages.success(request, 'İlanınız yayından kaldırıldı, teklif verenlere bildirim gönderildi.')
    else:
        messages.warning(request, 'Bu ilan zaten kapalı veya işlemde.')

    return redirect('job_detail', pk=pk)


@login_required
def edit_job(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)

    if job.status != 'open':
        messages.error(request, 'Yalnızca açık ilanlar düzenlenebilir.')
        return redirect('job_detail', pk=pk)

    if job.is_edited:
        messages.error(request, 'Her ilan yalnızca bir kez düzenlenebilir.')
        return redirect('job_detail', pk=pk)

    if job.proposals.exists():
        messages.error(request, 'Teklif alınmış ilanlar düzenlenemez.')
        return redirect('job_detail', pk=pk)

    from .forms import JobPostForm
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_edited = True
            updated.save()
            messages.success(request, 'İlanınız güncellendi. (Düzenleme hakkınız kullanıldı.)')
            return redirect('job_detail', pk=pk)
    else:
        form = JobPostForm(instance=job)

    from .models import JobCategory
    job_categories = JobCategory.objects.filter(is_active=True).values_list('title', flat=True)
    return render(request, 'forum/market/edit_job.html', {'form': form, 'job': job, 'job_categories': job_categories})


@login_required
@require_POST
def accept_proposal(request, pk, proposal_id):
    """Teklifi kabul et, ilanı askıya al"""
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)
    proposal = get_object_or_404(JobProposal, pk=proposal_id, job=job)

    if job.status != 'open':
        messages.warning(request, 'Bu ilan artık aktif değil.')
        return redirect('job_detail', pk=pk)

    # Reddedilecek teklifçileri update öncesi al
    rejected_proposals = list(
        job.proposals.exclude(pk=proposal_id).filter(status='pending').select_related('expert')
    )

    # Teklifi kabul et
    proposal.status = 'accepted'
    proposal.save()

    # Diğer teklifleri reddet
    job.proposals.exclude(pk=proposal_id).update(status='rejected')

    # İlanı askıya al
    job.status = 'in_progress'
    job.save()

    # AnalizBot'tan inbox bildirimleri gönder
    try:
        bot_user = User.objects.get(username='AnalizBot')
    except User.DoesNotExist:
        bot_user = request.user

    site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    # Kabul edilen teklifçiye bildirim
    PrivateMessage.objects.create(
        sender=bot_user,
        receiver=proposal.expert,
        message=(
            f'Tebrikler {proposal.expert.username}!\n\n'
            f'"{job.title}" ilanına verdiğiniz teklif kabul edildi.\n\n'
            f'Teklif Tutarı: {proposal.price} TL\n'
            f'Süre: {proposal.duration}\n\n'
            f'İlanı görüntülemek için: {site}/market/job/{job.pk}/'
        )
    )

    # Reddedilen teklifçilere bildirim
    for rp in rejected_proposals:
        PrivateMessage.objects.create(
            sender=bot_user,
            receiver=rp.expert,
            message=(
                f'Merhaba {rp.expert.username},\n\n'
                f'"{job.title}" ilanına verdiğiniz teklif değerlendirildi, '
                f'ancak bu sefer başka bir uzman tercih edildi.\n\n'
                f'Diğer açık ilanlar için: {site}/market/'
            )
        )

    messages.success(request, f'{proposal.expert.username} kullanıcısının teklifi kabul edildi. İlan askıya alındı.')
    return redirect('job_detail', pk=pk)


@login_required
@require_POST
def admin_manage_proposal(request, job_pk, proposal_id):
    """Adminlerin teklifleri yönetmesi (Silme/Reddetme)"""
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect('job_detail', pk=job_pk)

    job = get_object_or_404(FreelanceJob, pk=job_pk)
    proposal = get_object_or_404(JobProposal, pk=proposal_id, job=job)
    
    action = request.POST.get('action') # 'delete' or 'reject'
    reason_option = request.POST.get('reason_option')
    custom_reason = request.POST.get('custom_reason')
    
    # Sebep belirleme
    reason_map = {
        'spam': 'Spam veya yanıltıcı içerik.',
        'low_quality': 'Düşük kalite veya yetersiz açıklama.',
        'inappropriate': 'Uygunsuz dil veya içerik.',
        'irrelevant': 'İlanla ilgisiz teklif.',
        'other': custom_reason or 'Belirtilmedi.'
    }
    
    reason = reason_map.get(reason_option, custom_reason or 'Topluluk kurallarına aykırılık.')
    
    expert = proposal.expert
    
    if action == 'delete':
        # Silme işlemi
        proposal.delete()
        
        # Bildirim gönder (Mesaj)
        message = f"Sayın {expert.username},\n\n'{job.title}' ilanı için verdiğiniz teklif yöneticiler tarafından silinmiştir.\n\nSebep: {reason}\n\nLütfen topluluk kurallarına dikkat ediniz."
        
        PrivateMessage.objects.create(
            sender=request.user,
            receiver=expert,
            message=message
        )
        
        # Bildirim (Notification)
        Notification.objects.create(
            recipient=expert,
            sender=request.user,
            verb=f"Teklifiniz silindi: {reason}",
            content_type=ContentType.objects.get_for_model(job),
            object_id=job.id
        )
        
        messages.success(request, f"Teklif silindi ve kullanıcıya mesaj gönderildi.")
        
    elif action == 'reject':
        # Reddetme işlemi
        proposal.status = 'rejected'
        proposal.save()
        
        # Bildirim gönder (Mesaj)
        message = f"Sayın {expert.username},\n\n'{job.title}' ilanı için verdiğiniz teklif yöneticiler tarafından reddedilmiştir.\n\nSebep: {reason}"
        
        PrivateMessage.objects.create(
            sender=request.user,
            receiver=expert,
            message=message
        )

        # Bildirim (Notification)
        Notification.objects.create(
            recipient=expert,
            sender=request.user,
            verb=f"Teklifiniz reddedildi: {reason}",
            content_type=ContentType.objects.get_for_model(proposal),
            object_id=proposal.id
        )
        
        messages.success(request, f"Teklif reddedildi ve kullanıcıya mesaj gönderildi.")
        
    else:
        messages.warning(request, "Geçersiz işlem.")

    return redirect('job_detail', pk=job_pk)


@feature_required('market')
def job_detail(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)

    # Süresi geçmişse otomatik kapat
    job.expire_if_needed()

    # Görüntülenme sayısını artır
    job.views += 1
    job.save()

    site_settings = SiteSettings.load()
    proposal_count = job.proposals.count()

    user_proposal = None
    proposal_form = None

    # Teklif verme yetkisi kontrolü
    is_expert = JobProposal.can_propose(request.user)
    can_propose_reason = ""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        _, can_propose_reason = request.user.profile.can_propose()
    elif not request.user.is_authenticated:
        can_propose_reason = "Teklif verebilmek için giriş yapmalısınız."

    # 1. Teklifleri görme yetkisi
    if request.user == job.owner or request.user.is_superuser or request.user.is_staff:
        proposals = job.proposals.select_related('expert', 'expert__profile').all()
    elif site_settings.feature_proposal_price_privacy:
        proposals = None
    else:
        proposals = job.proposals.select_related('expert', 'expert__profile').all()

    # 2. Teklif verme formu işlemleri (İlan sahibi hariç herkes için kontrol edilir)

    # 2. Teklif verme formu işlemleri (İlan sahibi hariç herkes için kontrol edilir)
    if request.user != job.owner:
        if request.user.is_authenticated:
            user_proposal = JobProposal.objects.filter(job=job, expert=request.user).first()

        if is_expert and not user_proposal and job.status == 'open':
            if request.method == 'POST':
                proposal_form = ProposalForm(request.POST)
                if proposal_form.is_valid():
                    proposal = proposal_form.save(commit=False)
                    proposal.job = job
                    proposal.expert = request.user
                    proposal.save()

                    from .email_utils import send_proposal_notification
                    send_proposal_notification(proposal)

                    # İlan sahibinin inbox'ına teklif bildirimi düşür
                    # (email send_proposal_notification tarafından zaten gönderildi, _skip_email=True)
                    site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
                    _pm = PrivateMessage(
                        sender=request.user,
                        receiver=job.owner,
                        message=(
                            f'"{job.title}" ilanınıza yeni bir teklif geldi!\n\n'
                            f'Teklif Veren: {request.user.username}\n'
                            f'Teklif Tutarı: {proposal.price} TL\n'
                            f'Süre: {proposal.duration}\n\n'
                            f'Ön Yazı:\n{proposal.message[:500]}\n\n'
                            f'Teklifi değerlendirmek için: {site}/market/job/{job.pk}/'
                        )
                    )
                    _pm._skip_email = True
                    _pm.save()

                    messages.success(request, 'Teklifiniz başarıyla gönderildi!')
                    return redirect('job_detail', pk=pk)
            else:
                proposal_form = ProposalForm()

    is_liked = False
    is_saved = False
    if request.user.is_authenticated:
        is_liked = job.likes.filter(id=request.user.id).exists()
        is_saved = job.saved_by.filter(id=request.user.id).exists()

    # Benzer İlanlar (Aynı kategorideki diğer açık ilanlar)
    similar_jobs = FreelanceJob.objects.filter(
        category=job.category,
        status='open'
    ).exclude(pk=pk).order_by('-created_at')[:3]

    # Review bilgileri
    reviews = job.reviews.filter(is_approved=True).select_related('reviewer', 'reviewed_user')
    can_review = False
    own_review = None
    accepted_proposal = job.proposals.filter(status='accepted').first()
    if request.user.is_authenticated and accepted_proposal:
        # İlan sahibi veya kabul edilen uzman mı?
        is_owner = request.user == job.owner
        is_expert_accepted = request.user == accepted_proposal.expert
        if is_owner or is_expert_accepted:
            own_review = job.reviews.filter(reviewer=request.user).first()
        if (is_owner or is_expert_accepted) and job.status == 'in_progress':
            can_review = own_review is None

    return render(request, 'forum/market/job_detail.html', {
        'job': job,
        'proposals': proposals,
        'proposal_count': proposal_count,
        'user_proposal': user_proposal,
        'proposal_form': proposal_form,
        'is_liked': is_liked,
        'is_saved': is_saved,
        'is_expert': is_expert,
        'can_propose_reason': can_propose_reason,
        'similar_jobs': similar_jobs,
        'reviews': reviews,
        'can_review': can_review,
        'own_review': own_review,
        'accepted_proposal': accepted_proposal,
        'site_settings': site_settings,
    })

@login_required
@require_POST
def add_job_review(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)
    accepted_proposal = job.proposals.filter(status='accepted').first()

    if not accepted_proposal:
        messages.error(request, 'Bu ilan için değerlendirme yapılamaz.')
        return redirect('job_detail', pk=pk)

    # Yetki kontrolü
    is_owner = request.user == job.owner
    is_expert = request.user == accepted_proposal.expert
    if not (is_owner or is_expert):
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('job_detail', pk=pk)

    # Daha önce review yapmış mı?
    if job.reviews.filter(reviewer=request.user).exists():
        messages.warning(request, 'Zaten değerlendirme yapmışsınız.')
        return redirect('job_detail', pk=pk)

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')[:300]

    if not rating or int(rating) not in range(1, 6):
        messages.error(request, 'Geçerli bir puan seçin.')
        return redirect('job_detail', pk=pk)

    # Karşı tarafı bul
    reviewed_user = accepted_proposal.expert if is_owner else job.owner

    JobReview.objects.create(
        job=job,
        reviewer=request.user,
        reviewed_user=reviewed_user,
        rating=int(rating),
        comment=comment
    )

    try:
        bot_user = User.objects.get(username='AnalizBot')
    except User.DoesNotExist:
        bot_user = request.user
    site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    # Değerlendirilen kişiye bildirim: "X seni değerlendirdi"
    stars = '⭐' * int(rating)
    PrivateMessage.objects.create(
        sender=bot_user,
        receiver=reviewed_user,
        message=(
            f'Merhaba {reviewed_user.username},\n\n'
            f'"{job.title}" projesi için {request.user.username} sizi değerlendirdi.\n\n'
            f'Puan: {stars} ({rating}/5)'
            + (f'\nYorum: {comment}' if comment else '')
        )
    )

    # Karşı taraf henüz değerlendirme yapmadıysa "sen de yap" bildirimi
    other_party = accepted_proposal.expert if is_owner else job.owner
    other_has_reviewed = job.reviews.filter(reviewer=other_party).exists()
    if not other_has_reviewed:
        PrivateMessage.objects.create(
            sender=bot_user,
            receiver=other_party,
            message=(
                f'Merhaba {other_party.username},\n\n'
                f'"{job.title}" projesi için {request.user.username} değerlendirmesini tamamladı.\n\n'
                f'Projenin kapatılabilmesi için sizin de değerlendirme yapmanız gerekmektedir.\n\n'
                f'Değerlendirme yapmak için: {site}/market/job/{job.pk}/'
            )
        )

    messages.success(request, 'Değerlendirmeniz gönderildi. Admin onayından sonra yayınlanacak.')
    return redirect('job_detail', pk=pk)


@login_required
def my_jobs(request):
    # Kullanıcının açtığı ilanlar
    posted_jobs = FreelanceJob.objects.filter(owner=request.user).annotate(
        p_count=Count('proposals', distinct=True)
    ).order_by('-created_at')
    
    # Kullanıcının verdiği teklifler (Filtreleme eklendi)
    status_filter = request.GET.get('status', 'all')
    my_proposals = JobProposal.objects.filter(expert=request.user).select_related('job')
    
    if status_filter in ['pending', 'accepted', 'rejected']:
        my_proposals = my_proposals.filter(status=status_filter)
        
    my_proposals = my_proposals.order_by('-created_at')
    
    # Kullanıcının kaydettiği ilanlar
    saved_jobs = request.user.saved_jobs.annotate(
        p_count=Count('proposals', distinct=True)
    ).order_by('-created_at')
    
    return render(request, 'forum/market/my_jobs.html', {
        'posted_jobs': posted_jobs,
        'my_proposals': my_proposals,
        'saved_jobs': saved_jobs,
        'current_status': status_filter
    })

@login_required
def my_payments(request):
    """Kullanıcının ödeme geçmişi (İlanlar)"""
    job_payments = JobPayment.objects.filter(job__owner=request.user).select_related('job').order_by('-created_at')
    
    return render(request, 'forum/my_payments.html', {
        'job_payments': job_payments
    })

@login_required
def promote_job(request, pk):
    """İlanı vitrine taşıma (IBAN ile Ödeme)"""
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)

    # Vitrin sınırı kontrolü (max 4 ilan) - Süresi dolmamış olanları say
    MAX_FEATURED_JOBS = 4
    current_featured_count = FreelanceJob.objects.filter(
        is_featured=True,
        status='open',
        featured_until__gte=timezone.now()
    ).count()
    pending_count = FreelanceJob.objects.filter(
        feature_status='pending',
        status='open'
    ).exclude(pk=pk).count()

    if current_featured_count + pending_count >= MAX_FEATURED_JOBS:
        messages.warning(request, "Şu anda vitrin dolu. Lütfen daha sonra tekrar deneyiniz.")
        return redirect('job_detail', pk=pk)

    # Vitrin Paketleri
    packages = [
        {'days': 3, 'price': 250},
        {'days': 7, 'price': 400},
    ]

    # IBAN sayfasına yönlendir
    return render(request, 'forum/market/promote_job_iban.html', {
        'job': job,
        'packages': packages,
    })

@login_required
@require_POST
def mark_payment_transferred(request, pk):
    """Kullanıcının IBAN ödemesini yaptığını bildirmesi."""
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)

    # Paket bilgisi al
    package = request.POST.get('package', '3')
    packages = {'3': {'days': 3, 'price': 250}, '7': {'days': 7, 'price': 400}}
    selected = packages.get(package, packages['3'])

    # Ödeme kaydı kontrol et
    payment = JobPayment.objects.filter(job=job).order_by('-created_at').first()

    if payment and payment.status in ['success', 'pending_confirmation']:
        messages.info(request, "Daha önce ödeme bildirimi yapmışsınız. Onay bekleniyor.")
        return redirect('job_detail', pk=pk)

    if not payment:
        payment = JobPayment.objects.create(
            job=job,
            amount=selected['price'],
            duration_days=selected['days'],
            payment_id=f"IBAN-{uuid.uuid4().hex[:12].upper()}",
            conversation_id=f"IBAN-{job.pk}",
            status='pending_confirmation'
        )
    else:
        payment.amount = selected['price']
        payment.duration_days = selected['days']
        payment.status = 'pending_confirmation'
        payment.save()

    # İlanı onay bekleme durumuna al
    job.feature_status = 'pending'
    job.save()

    # Adminlere bildirim gönder
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            sender=request.user,
            verb=f"'{job.title}' (ID: {job.pk}) ilanı için IBAN ödemesi yapıldığını bildirdi.",
            target=job
        )

    messages.success(request, "Ödeme bildiriminiz alındı. Yönetici onayından sonra ilanınız vitrine taşınacaktır.")
    return redirect('job_detail', pk=pk)


# --- BÖLÜM DETAY ---
def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk)
    categories = section.categories.all()
    return render(request, 'forum/section_detail.html', {'section': section, 'categories': categories})

# --- KATEGORİ VE KONULAR ---
def category_topics(request, slug):
    category = get_object_or_404(Category, slug=slug)
    topics = category.topics.prefetch_related('tags').annotate(replies_count=Count('posts')).order_by('-is_pinned', '-created_at')
    # Bu kategoriye bağlı aktif çalışma odaları
    active_rooms = StudyRoom.objects.filter(
        category=category, status='active'
    ).annotate(member_cnt=Count('memberships', distinct=True)).order_by('-created_at')[:3]
    return render(request, 'forum/category_topics.html', {
        'category': category,
        'topics': topics,
        'active_rooms': active_rooms,
    })

# --- KONU DETAY VE CEVAP YAZMA ---
def topic_detail(request, pk):
    topic = get_object_or_404(Topic.objects.prefetch_related('tags'), pk=pk)
    topic.views += 1
    topic.save()

    posts = topic.posts.all().order_by('created_at')

    # Kullanıcının beğendiği post ID'leri
    user_liked_posts = []
    if request.user.is_authenticated:
        user_liked_posts = list(PostLike.objects.filter(
            user=request.user,
            post__in=posts
        ).values_list('post_id', flat=True))

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            # ✅ EMAIL BİLDİRİMİ GÖNDER
            send_topic_reply_notification(post, topic)

            return redirect('topic_detail', pk=pk)
    else:
        form = PostForm()

    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'posts': posts,
        'form': form,
        'user_liked_posts': user_liked_posts,
    })

# --- YENİ KONU AÇMA ---
@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def new_topic(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.starter = request.user
            topic.save()
            form.save_m2m()  # ManyToMany alanları (tags) kaydet
            # İlk mesajı oluştur
            Post.objects.create(
                topic=topic,
                message=form.cleaned_data['message'],
                created_by=request.user
            )
            return redirect('topic_detail', pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'forum/new_topic.html', {'category': category, 'form': form})

# --- KAYIT ---
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            # E-posta doğrulama token'ı oluştur ve gönder
            from .services.email_service import EmailService
            verification = EmailVerification.create_for_user(user)
            email_sent = EmailService.send_verification_email(user, verification)

            if email_sent:
                messages.success(request, 'Kayıt başarılı! Lütfen e-posta adresinizi doğrulayın. Doğrulama linki gönderildi.')
            else:
                messages.warning(request, 'Kayıt başarılı ancak doğrulama e-postası gönderilemedi. Profil sayfasından tekrar deneyebilirsiniz.')

            # Referral: davet kodu varsa bağlantıyı kaydet
            ref_code = request.session.pop('ref_code', None)
            if ref_code:
                _handle_referral_registration(request, user, ref_code)

            login(request, user)
            return redirect('verification_pending')
    else:
        form = RegisterForm()
    return render(request, 'forum/register.html', {'form': form})


def _handle_referral_registration(request, new_user, code):
    """Davet kodu ile kayıt olan kullanıcıyı referrer'a bağla."""
    from .models import ReferralCode, ReferralUse
    from .services.referral_service import notify_referral_registered
    from datetime import timedelta
    try:
        referral_code = ReferralCode.objects.select_related('user__profile').get(code=code)
        referrer = referral_code.user

        # Self-referral yasak
        if referrer == new_user:
            return

        # Referrer hesabı en az 7 gün eski ve e-postası doğrulanmış olmalı
        if (timezone.now() - referrer.date_joined).days < 7:
            return
        if not referrer.profile.email_verified:
            return

        # Kullanıcının zaten bir referrer'ı var mı?
        if ReferralUse.objects.filter(referred=new_user).exists():
            return

        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        ReferralUse.objects.create(referrer=referrer, referred=new_user, ip_address=ip)
        notify_referral_registered(referrer, new_user)
    except ReferralCode.DoesNotExist:
        pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Referral kayıt hatası: {e}")


# --- GİRİŞ (Rate Limited) ---
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='post:username', rate='3/m', method='POST', block=True)
def custom_login(request):
    """Rate limited login view"""
    from django.contrib.auth import authenticate, login as auth_login
    from django.contrib.auth.forms import AuthenticationForm
    from django.utils import timezone
    from django.utils.http import url_has_allowed_host_and_scheme
    from datetime import timedelta

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # EDU mail kontrolü
            _handle_edu_user(user)

            next_url = request.GET.get('next', 'home')
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                next_url = 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def _handle_edu_user(user):
    """EDU mail ile giriş yapanlara rozet ve teklif hakkı ver"""
    from django.utils import timezone
    from datetime import timedelta
    from .services.email_service import EmailService

    email = user.email.lower() if user.email else ''
    if not email.endswith('.edu') and not email.endswith('.edu.tr'):
        return

    profile = getattr(user, 'profile', None)
    if not profile:
        return

    # Zaten rozeti varsa atla
    if profile.badges.filter(slug='dogrulanmis-akademisyen').exists():
        return

    # Rozet ver
    badge = Badge.objects.filter(slug='dogrulanmis-akademisyen').first()
    if badge:
        profile.badges.add(badge)

    # 3 günlük teklif hakkı
    profile.edu_proposal_expires = timezone.now() + timedelta(days=3)
    profile.save(update_fields=['edu_proposal_expires'])

    # Admin DM gönder
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        PrivateMessage.objects.create(
            sender=admin_user,
            receiver=user,
            message=(
                f"Merhaba {user.username},\n\n"
                "EDU uzantılı mail adresiniz ile giriş yaptığınız için "
                "\"Doğrulanmış Akademisyen\" rozeti kazandınız! 🎓\n\n"
                "Ayrıca 3 gün boyunca teklif verme hakkına sahipsiniz.\n\n"
                "İyi çalışmalar,\nAnalizus Ekibi"
            )
        )

    # Mail gönder
    EmailService.send_edu_welcome_email(user)


# --- PROFİL DÜZENLE ---
@login_required
def profile_edit(request):
    user = request.user
    # Profil yoksa oluştur
    profile, created = Profile.objects.get_or_create(user=user)
    all_skills = JobCategory.objects.filter(is_active=True).order_by('order', 'title')

    if request.method == 'POST':
        # Kullanıcı Bilgileri
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Profil Bilgileri
        profile.title = request.POST.get('title', '')
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        
        # Akademik
        profile.university = request.POST.get('university', '')
        profile.department = request.POST.get('department', '')
        profile.academic_title = request.POST.get('academic_title', '')

        # Sosyal Medya
        profile.website = request.POST.get('website', '')
        linkedin = request.POST.get('linkedin', '')
        profile.linkedin = linkedin
        if linkedin and 'linkedin.com' in linkedin:
            profile.linkedin_verified = True
            profile.save()
            _check_and_award_trust_badge(request, user)
        else:
            profile.linkedin_verified = False
        profile.twitter = request.POST.get('twitter', '')
        profile.github = request.POST.get('github', '')
        profile.orcid = request.POST.get('orcid', '')
        profile.google_scholar = request.POST.get('google_scholar', '')

        # Telefon Numarası Güncelleme
        new_phone_number = request.POST.get('phone_number')
        if new_phone_number is not None:
            new_phone_number = new_phone_number.strip()
            if new_phone_number != profile.phone_number:
                if new_phone_number:
                    clean_number = new_phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                    if re.match(r'^05\d{9}$', clean_number):
                        profile.phone_number = clean_number
                        profile.phone_verified = True
                        _check_and_award_trust_badge(request, user)
                    else:
                        messages.error(request, "Geçersiz telefon numarası. Lütfen '05XXXXXXXXX' formatında giriniz.")
                else:
                    profile.phone_number = ""
                    profile.phone_verified = False

        # Dosyalar
        from django.conf import settings as django_settings
        from django.core.files.storage import default_storage
        logger.debug(f"DEBUG={django_settings.DEBUG}")
        logger.debug(f"DEFAULT_FILE_STORAGE={getattr(django_settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
        logger.debug(f"default_storage class: {default_storage.__class__.__name__}")
        logger.debug(f"request.FILES: {request.FILES}")
        logger.debug(f"'avatar' in FILES: {'avatar' in request.FILES}")
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            logger.debug(f"Avatar dosyası: {avatar_file.name}, boyut: {avatar_file.size}")
            logger.debug(f"Avatar field storage ÖNCE: {profile.avatar.storage.__class__.__name__ if profile.avatar else 'None'}")
            profile.avatar = avatar_file
            logger.debug(f"Avatar field storage SONRA: {profile.avatar.storage.__class__.__name__}")
        if 'cover_image' in request.FILES:
            profile.cover_image = request.FILES['cover_image']
        
        # Ayarlar
        profile.email_on_reply = request.POST.get('email_on_reply') == 'on'
        profile.email_on_private_message = request.POST.get('email_on_private_message') == 'on'
        profile.is_public = request.POST.get('is_public') == 'on'
        profile.show_email = request.POST.get('show_email') == 'on'

        # Uzmanlık alanları (JobCategory)
        selected_skills = request.POST.getlist('skills')
        profile.skills.set(selected_skills)

        try:
            profile.save()
            logger.debug(f"Profile saved. Avatar URL: {profile.avatar.url if profile.avatar else 'None'}")
            if profile.avatar:
                logger.debug(f"Avatar name: {profile.avatar.name}")
                logger.debug(f"Avatar storage: {profile.avatar.storage.__class__.__name__}")
                # S3'te var mı kontrol et
                try:
                    exists = profile.avatar.storage.exists(profile.avatar.name)
                    logger.debug(f"S3'te dosya var mı: {exists}")
                except Exception as check_err:
                    logger.warning(f"S3 kontrol hatası: {check_err}")
        except Exception as e:
            logger.error(f"Profile save error: {type(e).__name__}: {e}", exc_info=True)

        messages.success(request, "Profiliniz başarıyla güncellendi.")
        return redirect('profile_detail', username=user.username)
    
    return render(request, 'forum/profile_edit.html', {'user': user, 'profile': profile, 'all_skills': all_skills})

# --- GELEN KUTUSU ---
@feature_required('messaging')
@login_required
def inbox(request):
    # Okunmamış sayısını kaydet, sonra okundu yap
    unread_by_sender = {}
    for row in (PrivateMessage.objects
                .filter(receiver=request.user, is_read=False)
                .values('sender')
                .annotate(cnt=models.Count('id'))):
        unread_by_sender[row['sender']] = row['cnt']

    PrivateMessage.objects.filter(receiver=request.user, is_read=False).update(is_read=True)

    # Gönderilen + alınan tüm konuşmalar — her konuşma ortağı için en son mesaj
    seen = set()
    conversations = []
    qs = (PrivateMessage.objects
          .filter(Q(sender=request.user) | Q(receiver=request.user))
          .select_related('sender', 'sender__profile', 'receiver', 'receiver__profile')
          .order_by('-created_at'))
    for msg in qs:
        partner = msg.receiver if msg.sender == request.user else msg.sender
        if partner.id in seen:
            continue
        seen.add(partner.id)
        conversations.append({
            'sender': partner,
            'last_message': msg,
            'unread_count': unread_by_sender.get(partner.id, 0),
        })

    return render(request, 'forum/inbox.html', {'conversations': conversations})


# --- MESAJ POLLING API ---
@login_required
@require_GET
def api_chat_poll(request, username):
    """Chat sayfası için polling: son mesaj ID'sinden sonraki yeni mesajları döndür"""
    after_id = int(request.GET.get('after', 0))
    receiver = get_object_or_404(User, username=username)

    new_messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user),
        id__gt=after_id,
        is_deleted=False,
    ).order_by('created_at')[:50]

    data = []
    for msg in new_messages:
        attachment_url = ''
        attachment_type = ''
        if msg.attachment:
            attachment_url = msg.attachment.url
            attachment_type = msg.get_attachment_type() or ''

        data.append({
            'id': msg.id,
            'message': msg.message or '',
            'sender_id': msg.sender.id,
            'sender_username': msg.sender.username,
            'attachment_url': attachment_url,
            'attachment_name': msg.attachment_name or '',
            'attachment_type': attachment_type,
            'timestamp': timezone.localtime(msg.created_at).isoformat(),
        })

    return JsonResponse({'messages': data})


@login_required
@require_GET
def api_inbox_poll(request):
    """Inbox sayfası için polling: yeni okunmamış mesajları döndür"""
    after_id = int(request.GET.get('after', 0))

    new_messages = PrivateMessage.objects.filter(
        receiver=request.user,
        id__gt=after_id,
    ).select_related('sender').order_by('-created_at')[:20]

    data = []
    for msg in new_messages:
        data.append({
            'id': msg.id,
            'message': msg.message or '',
            'sender_username': msg.sender.username,
            'sender_profile_url': reverse('profile_detail', args=[msg.sender.username]),
            'reply_url': reverse('send_message', args=[msg.sender.username]),
            'created_at': timezone.localtime(msg.created_at).isoformat(),
            'is_read': msg.is_read,
        })

    return JsonResponse({'messages': data})

# --- ÖZEL MESAJ GÖNDER ---
@feature_required('messaging')
@login_required
@ratelimit(key='user', rate='30/h', method='POST', block=True)
def send_message(request, username):
    # E-posta doğrulama kontrolü
    if not request.user.profile.email_verified:
        messages.error(request, 'Özel mesaj gönderebilmek için lütfen e-posta adresinizi doğrulayın.')
        return redirect('verification_pending')

    receiver = get_object_or_404(User, username=username)

    # Hesabını silen / devre dışı bırakılmış kullanıcıya mesaj gönderilemez
    if not receiver.is_active:
        messages.error(request, 'Bu kullanıcı hesabını sildiği için mesaj gönderilemiyor.')
        return redirect('inbox')

    # Bot kullanıcılarına mesaj gönderilemez
    if receiver.username == 'AnalizBot':
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Bot kullanıcıya mesaj gönderilemez.'}, status=403)
            return redirect('send_message', username=username)

    # Sohbet geçmişini getir
    chat_messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        message_content = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')

        # En az biri olmalı
        if not message_content and not attachment:
            messages.error(request, 'Lütfen bir mesaj yazın veya dosya ekleyin.')
            return redirect('send_message', username=username)

        # Dosya validasyonu
        if attachment:
            if attachment.size > settings.MAX_UPLOAD_SIZE:
                messages.error(request, 'Dosya boyutu 5 MB\'ı geçemez.')
                return redirect('send_message', username=username)
            if attachment.content_type not in settings.ALLOWED_ATTACHMENT_TYPES:
                messages.error(request, 'Bu dosya türü desteklenmiyor. (Resim, PDF, Word, Excel, PowerPoint, CSV)')
                return redirect('send_message', username=username)

        # Mesaj oluştur
        msg = PrivateMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message_content,
            attachment=attachment,
            attachment_name=attachment.name if attachment else ''
        )

        # Email bildirimi signal (private_message_post_save) tarafından gönderiliyor

        # AJAX isteği ise JSON döndür (sayfa yenilenmez)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok', 'id': msg.id})

        messages.success(request, f"{receiver.username} kullanıcısına mesajınız gönderildi!")
        return redirect('send_message', username=username)

    return render(request, 'forum/send_message.html', {
        'receiver': receiver,
        'chat_messages': chat_messages,
        'is_bot': receiver.username == 'AnalizBot',
    })

def _chat_room_name(uid1, uid2):
    ids = sorted([uid1, uid2])
    return f'chat_{ids[0]}_{ids[1]}'


def _broadcast_chat(uid1, uid2, event):
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(_chat_room_name(uid1, uid2), event)
    except Exception:
        pass


@login_required
@require_POST
def api_edit_message(request, message_id):
    msg = get_object_or_404(PrivateMessage, id=message_id, sender=request.user, is_deleted=False)
    new_text = request.POST.get('message', '').strip()
    if not new_text:
        return JsonResponse({'ok': False, 'error': 'Mesaj boş olamaz.'}, status=400)
    if len(new_text) > 5000:
        return JsonResponse({'ok': False, 'error': 'Mesaj çok uzun.'}, status=400)
    from django.utils import timezone
    msg.message = new_text
    msg.edited_at = timezone.now()
    msg.save(update_fields=['message', 'edited_at'])
    _broadcast_chat(request.user.id, msg.receiver_id, {
        'type': 'message_edit',
        'message_id': msg.id,
        'message': new_text,
        'edited_at': timezone.localtime(msg.edited_at).isoformat(),
    })
    return JsonResponse({'ok': True, 'message': new_text, 'edited_at': timezone.localtime(msg.edited_at).isoformat()})


@login_required
@require_POST
def api_delete_message(request, message_id):
    msg = get_object_or_404(PrivateMessage, id=message_id, sender=request.user)
    msg.is_deleted = True
    msg.message = ''
    msg.save(update_fields=['is_deleted', 'message'])
    _broadcast_chat(request.user.id, msg.receiver_id, {
        'type': 'message_delete',
        'message_id': msg.id,
    })
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_delete_conversation(request, username):
    other = get_object_or_404(User, username=username)
    _broadcast_chat(request.user.id, other.id, {'type': 'conversation_delete'})
    PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)
    ).delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_edit_room_post(request, post_id):
    post = get_object_or_404(StudyRoomPost, id=post_id, author=request.user)
    new_text = request.POST.get('message', '').strip()
    if not new_text:
        return JsonResponse({'ok': False, 'error': 'Mesaj boş olamaz.'}, status=400)
    if len(new_text) > 5000:
        return JsonResponse({'ok': False, 'error': 'Mesaj çok uzun.'}, status=400)
    from django.utils import timezone
    post.message = new_text
    post.edited_at = timezone.now()
    post.save(update_fields=['message', 'edited_at'])
    return JsonResponse({'ok': True, 'message': new_text, 'edited_at': timezone.localtime(post.edited_at).isoformat()})


@login_required
@require_POST
def api_delete_room_post(request, post_id):
    post = get_object_or_404(StudyRoomPost, id=post_id, author=request.user)
    post.delete()  # post_delete signal S3 dosyasını temizler
    return JsonResponse({'ok': True})


def _check_and_award_trust_badge(request, user):
    """Tüm doğrulamalar tamamsa Güvenilir Üye rozeti verir"""
    from .signals import check_and_award_trust_badge
    profile = user.profile
    if check_and_award_trust_badge(profile):
        # Rozet yeni verildi
        # 50 Puan Hediye
        score, _ = QuizScore.objects.get_or_create(user=user)
        score.total_points += 50
        score.save()
        messages.success(request, 'TEBRİKLER! Tüm doğrulamaları tamamladığınız için "Güvenilir Üye" rozeti ve 50 Puan kazandınız.')

# --- PROFİL DETAY ---
@login_required
def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    is_staff = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    # GİZLİLİK KONTROLÜ: Profil herkese kapalıysa sadece sahip ve adminler tam görür
    if not is_owner and not is_staff:
        profile = getattr(profile_user, 'profile', None)
        if profile and not profile.is_public:
            return render(request, 'forum/profile_private.html', {
                'profile_user': profile_user,
            })

    # GİZLİLİK KONTROLÜ: E-posta gösterimi
    if not is_owner and hasattr(profile_user, 'profile') and not profile_user.profile.show_email:
        profile_user.email = ""

    # Doğrulama İşlemleri (POST)
    if request.method == 'POST' and request.user == profile_user:
        action = request.POST.get('action')
        if action == 'verify_phone':
            phone = request.POST.get('phone')
            if phone:
                clean_number = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                if re.match(r'^05\d{9}$', clean_number):
                    profile_user.profile.phone_number = clean_number
                    # Simülasyon: Gerçek SMS entegrasyonu olmadığı için direkt onaylıyoruz
                    profile_user.profile.phone_verified = True
                    profile_user.profile.save()
                    _check_and_award_trust_badge(request, profile_user)
                    messages.success(request, 'Telefon numaranız başarıyla kaydedildi.')
                else:
                    messages.error(request, "Geçersiz telefon numarası. Lütfen '05XXXXXXXXX' formatında giriniz.")
        elif action == 'verify_linkedin':
            linkedin_url = request.POST.get('linkedin')
            if linkedin_url:
                if 'linkedin.com' in linkedin_url:
                    profile_user.profile.linkedin = linkedin_url
                    profile_user.profile.linkedin_verified = True
                    profile_user.profile.save()
                    _check_and_award_trust_badge(request, profile_user)
                    messages.success(request, 'LinkedIn hesabınız başarıyla doğrulandı.')
                else:
                    messages.error(request, 'Geçersiz LinkedIn URL.')
        return redirect('profile_detail', username=username)

    posted_jobs = FreelanceJob.objects.filter(owner=profile_user).annotate(
        p_count=Count('proposals', distinct=True)
    ).order_by('-created_at')[:5]
    given_proposals = (
        JobProposal.objects.filter(expert=profile_user).select_related('job').order_by('-created_at')[:20]
        if is_owner else None
    )
    received_reviews = JobReview.objects.filter(reviewed_user=profile_user, is_approved=True).select_related('reviewer', 'job').order_by('-created_at')[:20]
    completed_projects = JobProposal.objects.filter(
        expert=profile_user, status='accepted', job__status__in=['in_progress', 'completed']
    ).select_related('job').prefetch_related('job__reviews').order_by('-created_at')[:12]

    # Yıldız ortalaması
    rating_stats = JobReview.objects.filter(reviewed_user=profile_user, is_approved=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # Kategori bazlı quiz istatistikleri
    quiz_stats = UserQuizAttempt.objects.filter(
        user=profile_user, 
        is_correct=True
    ).values('question__category').annotate(
        correct_count=Count('id')
    ).order_by('-correct_count')
    
    # Quiz Puanı ve Sıralaması
    user_score = QuizScore.objects.filter(user=profile_user).first()
    quiz_rank = None
    if user_score:
        quiz_rank = QuizScore.objects.filter(total_points__gt=user_score.total_points).count() + 1

    # Yetki bilgileri
    permissions = {}
    next_badge = None
    if hasattr(profile_user, 'profile'):
        permissions = profile_user.profile.get_permissions_summary()
        next_badge = profile_user.profile.get_next_badge_info()

    # Tüm rozetler ve kazanılma durumu
    all_badges = Badge.objects.filter(is_active=True).order_by('badge_type', '-points_required', 'name')
    user_badge_ids = set(profile_user.profile.badges.values_list('id', flat=True)) if hasattr(profile_user, 'profile') else set()

    return render(request, 'forum/profile_detail.html', {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'posted_jobs': posted_jobs,
        'given_proposals': given_proposals,
        'received_reviews': received_reviews,
        'completed_projects': completed_projects,
        'rating_stats': rating_stats,
        'quiz_stats': quiz_stats,
        'user_score': user_score,
        'quiz_rank': quiz_rank,
        'permissions': permissions,
        'next_badge': next_badge,
        'all_badges': all_badges,
        'user_badge_ids': user_badge_ids,
    })

# --- HESAP SİLME ---

@login_required
def account_delete_request(request):
    """Kullanıcıya email ile onay linki gönderir."""
    if request.method == 'POST':
        from django.contrib.auth import logout
        from django.utils import timezone
        from .email_utils import send_email_async
        import uuid, secrets
        from datetime import timedelta

        user = request.user
        profile = user.profile

        token = secrets.token_urlsafe(32)
        profile.deletion_token = token
        profile.deletion_token_expires_at = timezone.now() + timedelta(hours=24)
        profile.save(update_fields=['deletion_token', 'deletion_token_expires_at'])

        site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        confirm_url = f"{site_url}/account/delete/confirm/{token}/"

        html = f"""
        <p>Merhaba <strong>{user.username}</strong>,</p>
        <p>Analizus hesabınızı silmek için aşağıdaki butona tıklayın.</p>
        <p><a href="{confirm_url}" style="background:#dc2626;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">Hesabımı Kalıcı Olarak Sil</a></p>
        <p>Bu link <strong>24 saat</strong> geçerlidir. Talepte bulunmadıysanız bu emaili görmezden gelin.</p>
        <hr>
        <small>Analizus.com — {site_url}</small>
        """
        send_email_async(
            subject="Hesap Silme Onayı — Analizus",
            message=f"Hesabınızı silmek için şu linke gidin: {confirm_url}",
            recipient_list=[user.email],
            html_message=html,
        )
        messages.success(request, "Onay linki email adresinize gönderildi. 24 saat içinde tıklayarak işlemi tamamlayın.")
        return redirect('profile_detail', username=user.username)

    return render(request, 'forum/account_delete.html')


def account_delete_confirm(request, token):
    """Email'deki link ile gelir; hesabı devre dışı bırakır."""
    from django.contrib.auth import logout
    from django.utils import timezone
    from .models import Profile

    try:
        profile = Profile.objects.select_related('user').get(deletion_token=token)
    except Profile.DoesNotExist:
        messages.error(request, "Geçersiz veya süresi dolmuş link.")
        return redirect('home')

    if not profile.deletion_token_expires_at or timezone.now() > profile.deletion_token_expires_at:
        profile.deletion_token = ''
        profile.deletion_token_expires_at = None
        profile.save(update_fields=['deletion_token', 'deletion_token_expires_at'])
        messages.error(request, "Bu link süresi dolmuş. Lütfen yeniden talep edin.")
        return redirect('home')

    user = profile.user
    profile.deletion_requested_at = timezone.now()
    profile.deletion_token = ''
    profile.deletion_token_expires_at = None
    profile.save(update_fields=['deletion_requested_at', 'deletion_token', 'deletion_token_expires_at'])

    user.is_active = False
    user.save(update_fields=['is_active'])

    logout(request)
    messages.info(request, "Hesabınız devre dışı bırakıldı. Kişisel verileriniz 30 gün içinde kalıcı olarak silinecektir.")
    return redirect('home')


# --- DİĞER ---
def about(request):
    from .models import SuccessStory
    stories = SuccessStory.objects.filter(approval_status='approved').select_related('user__profile').order_by('-created_at')[:3]
    check = '<i class="bi bi-check-circle-fill text-success"></i>'
    partial = '<i class="bi bi-dash-circle text-warning"></i>'
    cross = '<i class="bi bi-x-circle text-danger"></i>'
    comparison_rows = [
        {'feature': 'Ücret',           'analizus': f'{check} Ücretsiz',         'spss': '~$1,500/yıl',    'smartpls': '~$900/yıl',  'excel': 'Ücretli'},
        {'feature': 'Kurulum',         'analizus': f'{check} Yok (tarayıcı)',   'spss': 'Gerekli',         'smartpls': 'Gerekli',     'excel': 'Gerekli'},
        {'feature': 'APA Rapor',       'analizus': f'{check} Otomatik',         'spss': f'{cross} Yok',    'smartpls': f'{cross} Yok','excel': f'{cross} Yok'},
        {'feature': 'PDF Çıktı',       'analizus': f'{check} Hazır',            'spss': f'{partial} Manuel','smartpls': f'{partial} Manuel','excel': f'{partial} Manuel'},
        {'feature': 'Cronbach Alpha',  'analizus': f'{check} Var',              'spss': f'{check} Var',    'smartpls': f'{check} Var','excel': f'{cross} Yok'},
        {'feature': 'Normallik Testi', 'analizus': f'{check} Var',              'spss': f'{check} Var',    'smartpls': f'{cross} Yok','excel': f'{cross} Yok'},
        {'feature': 'Uzman Desteği',   'analizus': f'{check} Pazar yeri',       'spss': f'{cross} Yok',    'smartpls': f'{cross} Yok','excel': f'{cross} Yok'},
        {'feature': 'Akademik Forum',  'analizus': f'{check} Var',              'spss': f'{cross} Yok',    'smartpls': f'{cross} Yok','excel': f'{cross} Yok'},
        {'feature': 'Türkçe Arayüz',   'analizus': f'{check} Tam Türkçe',       'spss': f'{partial} Kısmi','smartpls': f'{cross} İngilizce','excel': f'{partial} Kısmi'},
    ]
    return render(request, 'forum/about.html', {'stories': stories, 'comparison_rows': comparison_rows})

def how_it_works(request):
    """Nasıl Çalışır? sayfası"""
    return render(request, 'forum/how_it_works.html')

def tableau_dashboard(request):
    """TR Dizin Sağlık Araştırmaları Tableau Dashboard"""
    from tarama_seo_content import TARAMA_SEO_CONTENT
    return render(request, 'forum/tableau_dashboard.html', {
        'seo_guide': TARAMA_SEO_CONTENT.get('tableau'),
    })


def liderboard(request):
    """Haftalık ve tüm zamanlı liderboard"""
    from .models import QuizScore, UserQuizAttempt, Profile
    from django.db.models import Count, Sum, Q

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())  # Pazartesi

    # Haftalık quiz liderboard (bu hafta en fazla doğru cevap)
    weekly = (
        UserQuizAttempt.objects
        .filter(is_correct=True, created_at__date__gte=week_start)
        .values('user__username', 'user__profile__rank', 'user__id')
        .annotate(weekly_correct=Count('id'))
        .order_by('-weekly_correct')[:10]
    )

    # Tüm zamanlı reputation liderboard
    alltime = (
        Profile.objects
        .select_related('user')
        .filter(user__is_active=True)
        .order_by('-reputation')[:10]
    )

    # Mevcut kullanıcının sıraları
    user_weekly_rank = None
    user_alltime_rank = None
    if request.user.is_authenticated:
        weekly_correct = UserQuizAttempt.objects.filter(
            user=request.user, is_correct=True, created_at__date__gte=week_start
        ).count()
        user_weekly_rank = (
            UserQuizAttempt.objects
            .filter(is_correct=True, created_at__date__gte=week_start)
            .values('user')
            .annotate(cnt=Count('id'))
            .filter(cnt__gt=weekly_correct)
            .count() + 1
        )
        user_reputation = getattr(getattr(request.user, 'profile', None), 'reputation', 0)
        user_alltime_rank = Profile.objects.filter(reputation__gt=user_reputation).count() + 1

    return render(request, 'forum/liderboard.html', {
        'weekly': weekly,
        'alltime': alltime,
        'week_start': week_start,
        'user_weekly_rank': user_weekly_rank,
        'user_alltime_rank': user_alltime_rank,
    })

def contact(request):
    if request.method == 'POST':
        from .models import ContactMessage
        from .services.email_service import EmailService
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            # Admin'e bildirim emaili gönder
            admin_email = settings.DEFAULT_FROM_EMAIL
            html_content = (
                f"<h3>Yeni İletişim Formu Mesajı</h3>"
                f"<p><b>Ad:</b> {name}</p>"
                f"<p><b>Email:</b> {email}</p>"
                f"<p><b>Konu:</b> {subject}</p>"
                f"<p><b>Mesaj:</b></p><p>{message}</p>"
            )
            EmailService._send_email(
                to_email=admin_email,
                subject=f"[Analizus İletişim] {subject}",
                html_content=html_content,
                plain_content=f"Ad: {name}\nEmail: {email}\nKonu: {subject}\n\n{message}",
            )
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede dönüş yapacağız.')
        except Exception:
            messages.error(request, 'Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.')
        return redirect('contact')
    return render(request, 'forum/contact.html')


def gizlilik_politikasi(request):
    return render(request, 'forum/gizlilik_politikasi.html')


def proje_talebi(request):
    from .models import ProjectRequest
    from .services.email_service import EmailService

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        company = request.POST.get('company', '').strip()
        analysis_type = request.POST.get('analysis_type', '')
        description = request.POST.get('description', '').strip()
        data_size = request.POST.get('data_size', '')
        timeline = request.POST.get('timeline', '')
        source = request.POST.get('source', 'direct')

        if not all([name, email, analysis_type, description, data_size, timeline]):
            messages.error(request, 'Lütfen zorunlu alanları doldurunuz.')
            return redirect('proje_talebi')

        try:
            valid_sources = {c[0] for c in ProjectRequest.SOURCE_CHOICES}
            req = ProjectRequest.objects.create(
                name=name, email=email, company=company,
                analysis_type=analysis_type, description=description,
                data_size=data_size, timeline=timeline,
                source=source if source in valid_sources else 'direct',
            )

            # Admine bildirim
            admin_email = settings.ADMIN_NOTIFICATION_EMAIL
            analysis_label = dict(ProjectRequest.ANALYSIS_CHOICES).get(analysis_type, analysis_type)
            size_label = dict(ProjectRequest.DATA_SIZE_CHOICES).get(data_size, data_size)
            timeline_label = dict(ProjectRequest.TIMELINE_CHOICES).get(timeline, timeline)
            source_label = dict(ProjectRequest.SOURCE_CHOICES).get(req.source, req.source)
            admin_html = (
                f"<h3>Yeni Proje Talebi #{req.pk}</h3>"
                f"<p><b>Ad:</b> {name}</p>"
                f"<p><b>E-posta:</b> {email}</p>"
                f"<p><b>Kişi/Şirket/Kurum:</b> {company or '—'}</p>"
                f"<p><b>Kaynak:</b> {source_label}</p>"
                f"<p><b>Analiz Türü:</b> {analysis_label}</p>"
                f"<p><b>Veri Boyutu:</b> {size_label}</p>"
                f"<p><b>Süre Beklentisi:</b> {timeline_label}</p>"
                f"<p><b>Açıklama:</b></p><p>{description}</p>"
            )
            EmailService._send_email(
                to_email=admin_email,
                subject=f"[Analizus] Yeni Proje Talebi: {name} ({analysis_label})",
                html_content=admin_html,
                plain_content=f"Yeni talep #{req.pk}\nAd: {name}\nEmail: {email}\nŞirket: {company}\nTür: {analysis_label}\n\n{description}",
            )

            # Kullanıcıya onay
            user_html = (
                f"<p>Sayın {name},</p>"
                f"<p>Proje talebiniz başarıyla alındı. En kısa sürede sizinle iletişime geçeceğiz.</p>"
                f"<p><b>Talep Özeti:</b><br>"
                f"Analiz Türü: {analysis_label}<br>"
                f"Veri Boyutu: {size_label}<br>"
                f"Süre Beklentisi: {timeline_label}</p>"
                f"<p>— Analizus Ekibi</p>"
            )
            EmailService._send_email(
                to_email=email,
                subject="Proje talebiniz alındı — Analizus",
                html_content=user_html,
                plain_content=f"Sayın {name},\n\nProje talebiniz alındı. En kısa sürede sizinle iletişime geçeceğiz.\n\n— Analizus Ekibi",
            )

            messages.success(request, 'Talebiniz alındı! En kısa sürede size dönüş yapacağız.')
        except Exception:
            messages.error(request, 'Bir hata oluştu, lütfen tekrar deneyin.')
        return redirect('proje_talebi')

    source = request.GET.get('source', 'direct')

    completed_count = FreelanceJob.objects.filter(status='completed').count()
    total_users = User.objects.count()

    recent_jobs_qs = (
        FreelanceJob.objects
        .filter(status='completed')
        .select_related('category')
        .order_by('-updated_at')[:4]
    )
    recent_completed = []
    for job in recent_jobs_qs:
        days = max((job.updated_at - job.created_at).days, 1)
        if days <= 7:
            duration = f"{days} günde"
        elif days <= 30:
            duration = f"{days // 7} haftada"
        else:
            duration = f"{days // 30} ayda"
        recent_completed.append({
            'category': job.category.title if job.category else 'Veri Analizi',
            'duration': duration,
        })

    return render(request, 'forum/proje_talebi.html', {
        'source': source,
        'completed_count': completed_count,
        'total_users': total_users,
        'recent_completed': recent_completed,
    })


@feature_required('agentic_landing')
def ai_cozumler(request):
    return render(request, 'forum/ai_cozumler.html', {})


def search_result(request):
    """Arama sonuçları"""
    query = request.GET.get('q', '').strip()

    topics = []
    users = []

    if query and len(query) >= 2:
        # Konularda ara (başlık ve içerik)
        topics = Topic.objects.filter(
            Q(subject__icontains=query) |
            Q(posts__message__icontains=query)
        ).distinct().select_related('starter', 'category').order_by('-created_at')[:20]

        # Kullanıcılarda ara
        users = User.objects.filter(
            Q(username__icontains=query)
        ).order_by('username')[:10]

    context = {
        'query': query,
        'topics': topics,
        'users': users,
        'topics_count': len(topics),
        'users_count': len(users),
    }

    return render(request, 'forum/search_results.html', context)

def summarize_topic(request, pk):
    return redirect('topic_detail', pk=pk)

# --- LIKE SİSTEMİ ---
@login_required
def toggle_like(request, post_id):
    """Post beğenme/beğenmekten vazgeçme"""
    post = get_object_or_404(Post, pk=post_id)

    # Kullanıcı daha önce beğenmiş mi?
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)

    if created:
        # Yeni like - sayacı artır
        post.likes += 1
        post.save()
        messages.success(request, "Yanıtı beğendiniz!")
    else:
        # Zaten like var - kaldır
        like.delete()
        post.likes = max(0, post.likes - 1)
        post.save()
        messages.info(request, "Beğeniniz kaldırıldı.")

    return redirect('topic_detail', pk=post.topic.pk)


# --- BİLDİRİM API (AJAX) ---
@login_required
@require_GET
def get_notifications(request):
    """Kullanıcının okunmamış bildirimlerini JSON olarak döndür"""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:10]

    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'message': notif.verb,
            'url': notif.get_url(),
            'created_at': timezone.localtime(notif.created_at).strftime('%d.%m.%Y %H:%M'),
            'sender': notif.sender.username if notif.sender else None,
        })

    # Toplam okunmamış bildirim sayısı
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        'notifications': data,
        'unread_count': unread_count
    })


@login_required
def mark_notification_read(request, notification_id):
    """Bildirimi okundu olarak işaretle"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


@login_required
def mark_all_notifications_read(request):
    """Tüm bildirimleri okundu olarak işaretle"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


# --- KULLANICI ARAMA API (@mention autocomplete) ---
@login_required
@require_GET
def user_search_api(request):
    """@mention autocomplete için kullanıcı arama endpoint'i"""
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'users': []})
    users = User.objects.filter(
        username__istartswith=q
    ).exclude(
        id=request.user.id
    ).select_related('profile')[:5]
    data = []
    for u in users:
        avatar_url = ''
        rank = 'Üye'
        if hasattr(u, 'profile'):
            if u.profile.avatar:
                avatar_url = u.profile.avatar.url
            rank = u.profile.get_rank_display()
        data.append({
            'username': u.username,
            'avatar_url': avatar_url,
            'rank': rank,
        })
    return JsonResponse({'users': data})


def _anon_ai_cache_key(request):
    """Cookie bazlı anonim AI kullanım cache key'i. (cache_key, anon_id) döner."""
    import uuid as _uuid
    anon_id = request.COOKIES.get('ax_anon_id') or str(_uuid.uuid4())
    return f"ai_usage_anon_{anon_id}_{timezone.now().date()}", anon_id


def _set_anon_cookie(response, anon_id):
    """Persistent anonim kimlik cookie'sini response'a ekler (1 gün)."""
    response.set_cookie('ax_anon_id', anon_id, max_age=86400,
                        samesite='Lax', httponly=True)
    return response


# --- AI ASISTAN ---
@feature_required('ai_assistant')
def ai_assistant(request):
    """AI Asistan sayfası — giriş yapanlar 30, anonim kullanıcılar 3 soru/gün"""
    from .services.ai_service import groq_service
    from django.core.cache import cache

    is_authenticated = request.user.is_authenticated

    if is_authenticated:
        cache_key = f"ai_usage_{request.user.id}_{timezone.now().date()}"
        daily_limit = 30
        anon_id = None
    else:
        cache_key, anon_id = _anon_ai_cache_key(request)
        daily_limit = 3

    usage_count = cache.get(cache_key, 0)

    context = {
        'usage_count': usage_count,
        'daily_limit': daily_limit,
        'remaining': max(0, daily_limit - usage_count),
        'ai_available': groq_service.is_available(),
        'is_authenticated': is_authenticated,
    }

    def _render(ctx):
        resp = render(request, 'forum/ai_assistant.html', ctx)
        return _set_anon_cookie(resp, anon_id) if anon_id else resp

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            messages.error(request, 'Lütfen bir soru girin.')
            return _render(context)

        if usage_count >= daily_limit:
            if is_authenticated:
                messages.warning(request, f'Günlük {daily_limit} soru limitinizi doldurdunuz. Yarın tekrar deneyin.')
            else:
                messages.warning(request, f'Günlük anonim limit ({daily_limit} soru) doldu. Üye olarak 30 soruya kadar kullanabilirsiniz.')
            return _render(context)

        if not groq_service.is_available():
            messages.error(request, 'AI servisi şu anda kullanılamıyor.')
            return _render(context)

        result = groq_service.generate_response(user_message)

        if result['success']:
            cache.set(cache_key, usage_count + 1, 60 * 60 * 24)
            context['ai_response'] = result['response']
            context['usage_count'] = usage_count + 1
            context['remaining'] = max(0, daily_limit - usage_count - 1)
        else:
            messages.error(request, result['error'])

    return _render(context)


@require_POST
@feature_required('ai_assistant')
def api_ai_chat(request):
    """Floating widget için AI sohbet API endpoint'i — JSON döner"""
    from .services.ai_service import groq_service
    from django.core.cache import cache
    import json

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'error': 'Geçersiz istek.'}, status=400)

    if not user_message:
        return JsonResponse({'success': False, 'error': 'Mesaj boş olamaz.'})

    if len(user_message) > 2000:
        return JsonResponse({'success': False, 'error': 'Mesaj çok uzun (max 2000 karakter).'})

    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        cache_key = f"ai_usage_{request.user.id}_{timezone.now().date()}"
        daily_limit = 30
        anon_id = None
    else:
        cache_key, anon_id = _anon_ai_cache_key(request)
        daily_limit = 3

    usage_count = cache.get(cache_key, 0)

    def _json(data, **kwargs):
        resp = JsonResponse(data, **kwargs)
        return _set_anon_cookie(resp, anon_id) if anon_id else resp

    if usage_count >= daily_limit:
        return _json({
            'success': False,
            'limit_reached': True,
            'error': f'Günlük {daily_limit} soru limitine ulaştınız.',
            'remaining': 0,
            'daily_limit': daily_limit,
            'is_authenticated': is_authenticated,
        })

    if not groq_service.is_available():
        return _json({'success': False, 'error': 'AI servisi şu anda kullanılamıyor.'})

    result = groq_service.generate_response(user_message)

    if result['success']:
        cache.set(cache_key, usage_count + 1, 60 * 60 * 24)
        new_remaining = max(0, daily_limit - usage_count - 1)
        return _json({
            'success': True,
            'response': result['response'],
            'remaining': new_remaining,
            'daily_limit': daily_limit,
        })

    return _json({'success': False, 'error': result['error']})


@login_required
def ai_suggest_answer(request, topic_id):
    """Forum konusu için AI yanıt önerisi"""
    from .services.ai_service import groq_service

    topic = get_object_or_404(Topic, pk=topic_id)

    if not groq_service.is_available():
        return JsonResponse({'error': 'AI servisi kullanılamıyor'}, status=503)

    # Konunun ilk postunu al
    first_post = topic.posts.first()
    content = first_post.message if first_post else topic.subject

    result = groq_service.suggest_answer(topic.subject, content)

    if result['success']:
        return JsonResponse({'suggestion': result['suggestion']})
    else:
        return JsonResponse({'error': result['error']}, status=500)


# --- E-POSTA DOĞRULAMA ---
@login_required
def verification_pending(request):
    """E-posta doğrulama bekleniyor sayfası"""
    profile = request.user.profile

    if profile.email_verified:
        messages.info(request, 'E-posta adresiniz zaten doğrulanmış.')
        return redirect('home')

    return render(request, 'forum/verification_pending.html')


def verify_email(request, token):
    """E-posta doğrulama linki işleme"""
    from .services.email_service import EmailService

    try:
        verification = EmailVerification.objects.get(token=token)
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Geçersiz doğrulama linki.')
        return redirect('home')

    if not verification.is_valid():
        messages.error(request, 'Bu doğrulama linki süresi dolmuş veya daha önce kullanılmış.')
        return redirect('home')

    # Kullanıcıyı doğrula
    user = verification.user
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.email_verified = True
    profile.save()

    # Rozet kontrolü
    _check_and_award_trust_badge(request, user)

    # Referral: e-posta doğrulandı, koşulları dene (48h/quiz henüz sağlanmamış olabilir)
    try:
        from .models import ReferralUse
        from .services.referral_service import check_and_award_referral
        referral = ReferralUse.objects.filter(referred=user, rewarded=False, flagged=False).first()
        if referral:
            referral.email_verified_at = timezone.now()
            referral.save(update_fields=['email_verified_at'])
            check_and_award_referral(referral)
    except Exception:
        pass

    # Token'ı kullanılmış olarak işaretle
    verification.is_used = True
    verification.save()

    # Hoş geldin e-postası gönder
    EmailService.send_welcome_email(user)

    messages.success(request, 'E-posta adresiniz başarıyla doğrulandı! Hoş geldiniz.')

    # Kullanıcı giriş yapmamışsa giriş yap
    if not request.user.is_authenticated:
        login(request, user)

    # Onboarding tamamlanmamışsa yönlendir
    if not profile.onboarding_completed:
        return redirect('onboarding')

    return redirect('home')


@login_required
@ratelimit(key='user', rate='3/h', method=['GET', 'POST'], block=True)
def resend_verification(request):
    """Doğrulama e-postasını tekrar gönder"""
    from .services.email_service import EmailService

    profile = request.user.profile

    if profile.email_verified:
        messages.info(request, 'E-posta adresiniz zaten doğrulanmış.')
        return redirect('home')

    # Yeni token oluştur ve gönder
    verification = EmailVerification.create_for_user(request.user)
    email_sent = EmailService.send_verification_email(request.user, verification)

    if email_sent:
        messages.success(request, 'Doğrulama e-postası tekrar gönderildi. Lütfen e-posta kutunuzu kontrol edin.')
    else:
        messages.error(request, 'E-posta gönderilemedi. Lütfen daha sonra tekrar deneyin.')

    return redirect('verification_pending')


# --- ADMİN ACTIONS (Django admin dashboard'dan kullanılıyor) ---
@staff_member_required
def admin_verify_linkedin(request, user_id):
    user_to_verify = get_object_or_404(User, id=user_id)
    profile = user_to_verify.profile
    
    profile.linkedin_verified = True
    profile.save()
    
    # Check for trust badge
    _check_and_award_trust_badge(request, user_to_verify)
    
    messages.success(request, f"{user_to_verify.username} kullanıcısının LinkedIn profili onaylandı.")
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))


@staff_member_required
@require_POST
def dashboard_approve_story(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    action = request.POST.get('action', 'approve')
    if action == 'reject':
        story.approval_status = 'rejected'
        messages.info(request, f"{story.user.username} hikayesi reddedildi.")
    else:
        story.approval_status = 'approved'
        messages.success(request, f"{story.user.username} hikayesi onaylandı.")
    story.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))


@staff_member_required
@require_POST
def dashboard_approve_review(request, pk):
    review = get_object_or_404(JobReview, pk=pk)
    review.is_approved = True
    review.save()

    try:
        bot_user = User.objects.get(username='AnalizBot')
    except User.DoesNotExist:
        bot_user = request.user
    PrivateMessage.objects.create(
        sender=bot_user,
        receiver=review.reviewer,
        message=(
            f'Merhaba {review.reviewer.username},\n\n'
            f'"{review.job.title}" projesi için yaptığınız değerlendirme onaylandı ve yayınlandı.'
        )
    )

    messages.success(request, f"{review.reviewer.username} değerlendirmesi onaylandı.")
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))


@staff_member_required
@require_POST
def dashboard_approve_donation(request, pk):
    from .models import Donation
    donation = get_object_or_404(Donation, pk=pk)
    donation.status = 'completed'
    donation.completed_at = timezone.now()
    donation.save()
    # Model'deki grant_premium() metodunu kullan
    if donation.user:
        donation.grant_premium()
    messages.success(request, f"Bağış onaylandı. {donation.premium_days_granted} gün premium verildi.")
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))


@staff_member_required
@require_POST
def dashboard_mark_contact_read(request, pk):
    from .models import ContactMessage
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))


@staff_member_required
def dashboard_export_csv(request):
    import csv
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta

    export_type = request.GET.get('type', 'users')
    today = timezone.now().date()

    if export_type == 'istatistik':
        try:
            from istatistik.models import IstatistikJob
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="analiz_kullanim.csv"'
            response.write('\ufeff')
            writer = csv.writer(response)
            writer.writerow(['Tarih', 'Araç', 'Kullanıcı', 'Demo mi', 'Durum'])
            qs = IstatistikJob.objects.select_related('user').order_by('-created_at')[:5000]
            for job in qs:
                writer.writerow([
                    timezone.localtime(job.created_at).strftime('%Y-%m-%d %H:%M'),
                    job.get_tool_display(),
                    job.user.username if job.user else 'Anonim',
                    'Evet' if job.is_demo else 'Hayır',
                    job.get_status_display(),
                ])
            return response
        except Exception as e:
            from django.http import HttpResponseServerError
            return HttpResponseServerError(f'CSV oluşturulamadı: {e}')
    else:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="kullanici_istatistikleri.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Kullanıcı Adı', 'E-posta', 'Kayıt Tarihi', 'Son Giriş', 'E-posta Doğrulandı', 'Puan'])
        qs = User.objects.select_related('profile').order_by('-date_joined')
        for u in qs:
            profile = getattr(u, 'profile', None)
            writer.writerow([
                u.username,
                u.email,
                u.date_joined.strftime('%Y-%m-%d'),
                u.last_login.strftime('%Y-%m-%d') if u.last_login else '',
                'Evet' if (profile and profile.email_verified) else 'Hayır',
                profile.score if profile else 0,
            ])
        return response


# --- API: QUIZ & STORIES ---
def api_get_quiz_question(request):
    """
    Rastgele aktif bir quiz sorusu getirir.
    Giriş yapmış kullanıcılara bugün cevaplanmamış sorular gösterilir (günlük 20 limit).
    Anonim kullanıcılara herhangi bir aktif soru gösterilir.
    """
    try:
        if request.user.is_authenticated:
            today = timezone.now().date()
            answered_today_ids = UserQuizAttempt.objects.filter(
                user=request.user,
                created_at__date=today
            ).values_list('question_id', flat=True)

            if answered_today_ids.count() >= 20:
                return JsonResponse({'success': False, 'error': 'Günlük 20 soru limitinizi doldurdunuz. Yarın tekrar bekleriz!'})

            question = QuizQuestion.objects.filter(is_active=True).exclude(id__in=answered_today_ids).order_by('?').first()
        else:
            answered_today_ids = []
            question = QuizQuestion.objects.filter(is_active=True).order_by('?').first()

        if question:
            data = {
                'id': question.id,
                'question': question.question,
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d
                },
                'category': question.get_category_display(),
                'difficulty': question.get_difficulty_display()
            }
            return JsonResponse({'success': True, 'question': data})
        else:
            if request.user.is_authenticated and QuizQuestion.objects.filter(is_active=True).exists():
                return JsonResponse({'success': False, 'error': 'Bugünlük çözülecek soru kalmadı. Yarın tekrar bekleriz!'})
            else:
                return JsonResponse({'success': False, 'error': 'Sistemde henüz aktif bir soru bulunmuyor.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Bir hata oluştu: {str(e)}'})

@csrf_exempt
def api_submit_quiz_answer(request):
    """Quiz cevabını kontrol eder ve puan/rozet verir"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Puan kazanmak için giriş yapmalısınız.', 'requires_login': True})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer = data.get('answer')
            
            question = get_object_or_404(QuizQuestion, pk=question_id)
            is_correct = (answer == question.correct_answer)
            
            # 1. Denemeyi Kaydet (Kategori takibi için)
            # models.py'ye UserQuizAttempt eklediğinizi varsayıyoruz
            UserQuizAttempt.objects.create(user=request.user, question=question, is_correct=is_correct)

            # Puan Güncelleme
            score, created = QuizScore.objects.get_or_create(user=request.user)
            score.total_answers += 1
            if is_correct:
                score.correct_answers += 1
                score.total_points += 10
                score.streak += 1
                
                # ANA PROFİL PUANINI GÜNCELLE
                try:
                    profile = request.user.profile
                    profile.reputation += 10
                    profile.save(update_fields=['reputation'])
                    # Puan bazlı rozetleri ve rütbeyi güncelle
                    profile.check_and_award_badges()
                    profile.update_rank()
                except Profile.DoesNotExist:
                    pass  # Profil yoksa görmezden gel (normalde olmamalı)
            else:
                score.streak = 0
            score.last_played = timezone.now()
            score.save()
            
            # Rozet Kontrolü
            badge_awarded = None
            
            if is_correct and score.correct_answers > 0:
                
                # --- KATEGORİ BAZLI ROZETLER ---
                category_correct_count = UserQuizAttempt.objects.filter(
                    user=request.user,
                    question__category=question.category,
                    is_correct=True
                ).count()

                # Rozet kontrolü signals üzerinden yapılır (eşik: 50 doğru)
                from .signals import check_and_award_quiz_badges
                check_and_award_quiz_badges(
                    request.user.profile,
                    category=question.category,
                    correct_count=category_correct_count,
                    total_correct=score.correct_answers
                )

                # Yeni kazanılan rozeti kullanıcıya bildir
                if category_correct_count == 50:
                    category_badge_map = {
                        'SPSS': 'SPSS Uzmanı', 'spss': 'SPSS Uzmanı',
                        'Python': 'Python Ninja', 'python': 'Python Ninja',
                        'R': 'R Üstadı', 'r': 'R Üstadı',
                        'statistics': 'İstatistik Ustası', 'İstatistik': 'İstatistik Ustası',
                    }
                    badge_name = category_badge_map.get(str(question.category))
                    if badge_name:
                        badge_awarded = badge_name

                if score.correct_answers == 1000:
                    badge_awarded = 'Quiz Efsanesi'


            correct_answer_text = getattr(question, f'option_{question.correct_answer.lower()}', '')
            return JsonResponse({
                'success': True,
                'is_correct': is_correct,
                'correct_answer': question.correct_answer,
                'correct_answer_text': correct_answer_text,
                'explanation': question.explanation,
                'new_score': score.total_points,
                'total_correct': score.correct_answers,
                'badge_awarded': badge_awarded
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def api_get_profile_summary(request, username):
    """Kullanıcı profil özetini modal için getirir"""
    profile_user = get_object_or_404(User, username=username)
    
    html = render_to_string('forum/partials/profile_modal_content.html', {
        'profile_user': profile_user, 
        'request': request
    })
    return JsonResponse({'success': True, 'html': html})

def api_get_featured_story(request):
    """Haftanın başarı hikayesini getirir (Modal için)"""
    story = SuccessStory.objects.filter(is_featured=True, approval_status='approved').first()
    if not story:
        story = SuccessStory.objects.filter(approval_status='approved').order_by('?').first()
    
    if story:
        html = render_to_string('forum/partials/story_modal_content.html', {'story': story})
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False})

@login_required
def api_toggle_follow(request, username):
    """Kullanıcı takip etme/bırakma"""
    # E-posta doğrulama kontrolü
    if not request.user.profile.email_verified:
        return JsonResponse({'success': False, 'error': 'Kullanıcıları takip edebilmek için lütfen e-posta adresinizi doğrulayın.'})

    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'success': False, 'error': 'Kendinizi takip edemezsiniz.'})
    
    user_profile = request.user.profile
    target_profile = target_user.profile
    
    if target_profile in user_profile.following.all():
        user_profile.following.remove(target_profile)
        is_following = False
    else:
        user_profile.following.add(target_profile)
        is_following = True
        
        # Bildirim gönder
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            verb="sizi takip etmeye başladı",
            content_type=ContentType.objects.get_for_model(target_user),
            object_id=target_user.id
        )
        
    return JsonResponse({'success': True, 'is_following': is_following, 'follower_count': target_profile.followers.count()})


# --- BAĞIŞ SİSTEMİ ---
from .models import Donation, DonationTier
import uuid

def donation_widget_data(request):
    """Bağış widget'ı için veri döndürür (AJAX)"""
    total = Donation.get_total_donations()
    recent_donors = Donation.get_recent_donors(5)

    donors_data = []
    for d in recent_donors:
        donors_data.append({
            'name': d.name or (d.user.username if d.user else 'Anonim'),
            'amount': float(d.amount),
            'date': timezone.localtime(d.completed_at).strftime('%d.%m.%Y') if d.completed_at else '',
        })

    return JsonResponse({
        'total': float(total),
        'recent_donors': donors_data,
        'donor_count': Donation.objects.filter(status='completed').count(),
    })




def donation_success(request):
    """Başarılı bağış sayfası"""
    payment_id = request.GET.get('payment_id')
    donation = None

    if payment_id:
        try:
            donation = Donation.objects.get(payment_id=payment_id)
        except Donation.DoesNotExist:
            pass

    context = {
        'donation': donation,
        'premium_days': donation.get_premium_days() if donation else 0,
    }
    return render(request, 'forum/donation_success.html', context)



# ═══════════════════════════════════════════════════════════════════════════════
# BLOG SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════

@feature_required('blog')
def blog_list(request):
    """Blog ana sayfası - yazı listesi"""
    qs = request.META.get('QUERY_STRING', '')
    if qs.endswith('&'):
        return redirect(request.path + '?' + qs.rstrip('&'), permanent=True)

    # ?level= parametresi SEO'da duplicate üretir — 301 ile temizle
    level_filter_early = request.GET.get('level', '')
    if level_filter_early:
        category_slug_early = request.GET.get('category', '')
        if category_slug_early:
            return redirect(f"{request.path}?category={category_slug_early}", permanent=True)
        return redirect(request.path, permanent=True)

    posts = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    # Arama
    search_query = request.GET.get('q', '').strip()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Kategori filtresi
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Etiket filtresi
    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    # Seviye filtresi
    level_filter = request.GET.get('level', '')
    if level_filter:
        posts = posts.filter(level=level_filter)

    # Öne çıkan yazılar (filtre yoksa göster)
    featured_posts = []
    if not search_query and not category_slug and not tag_slug and not level_filter:
        featured_posts = BlogPost.objects.filter(
            status='published', is_featured=True
        ).select_related('author', 'category')[:3]

    # Kategoriler
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)

    # Etiketler
    tags = BlogTag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).order_by('name')

    # Popüler yazılar
    popular_posts = BlogPost.objects.filter(status='published').order_by('-views')[:5]

    # Sayfalama
    posts = posts.order_by('-published_at')
    paginator = Paginator(posts, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'featured_posts': featured_posts,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_level': level_filter,
        'search_query': search_query,
    }
    return render(request, 'forum/blog/blog_list.html', context)


@feature_required('blog')
def blog_detail(request, slug):
    """Blog yazı detay sayfası"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # Görüntülenme sayısını artır
    post.views += 1
    post.save(update_fields=['views'])

    # Kullanıcı beğenmiş mi?
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(pk=request.user.pk).exists()

    # İlgili yazılar (aynı kategoriden, en yeni 3)
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk).select_related('category').order_by('-published_at')[:3]

    # Sidebar: aynı kategoriden son 5 yazı
    category_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk).order_by('-published_at')[:5]

    # Sidebar: en çok okunan 5 yazı
    popular_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(pk=post.pk).order_by('-views')[:5]

    # Sidebar: kategoriler
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)

    context = {
        'post': post,
        'is_liked': is_liked,
        'related_posts': related_posts,
        'category_posts': category_posts,
        'popular_posts': popular_posts,
        'categories': categories,
    }
    return render(request, 'forum/blog/blog_detail.html', context)


@feature_required('blog')
@login_required
@require_POST
def blog_like(request, slug):
    """Blog yazısını beğen/beğeniyi kaldır"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': post.total_likes})

    return redirect('blog_detail', slug=slug)


@feature_required('blog')
@login_required
def blog_create(request):
    """Blog yazısı oluşturma - Badge gerektirir"""
    # Blog yazma yetkisi kontrolü
    profile = request.user.profile
    can_write = profile.badges.filter(can_write_blog=True).exists()

    if not can_write:
        messages.warning(request, "Blog yazmak için gerekli rozete sahip değilsiniz.")
        return redirect('blog_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category_id = request.POST.get('category')

        if not title or not content:
            messages.error(request, "Başlık ve içerik zorunludur.")
        else:
            from django.utils.text import slugify
            slug = slugify(title)
            # Slug benzersizliği
            base_slug = slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            post = BlogPost.objects.create(
                title=title,
                slug=slug,
                content=content,
                author=request.user,
                category_id=category_id if category_id else None,
                status='draft'  # Admin onayı bekleyecek
            )
            messages.success(request, "Blog yazınız oluşturuldu. Yönetici onayından sonra yayınlanacaktır.")
            return redirect('blog_list')

    categories = BlogCategory.objects.all()
    return render(request, 'forum/blog/blog_create.html', {'categories': categories})


# --- DESTEK/BAĞI APISI ---
@login_required
@require_POST
def send_support_email(request):
    """Kullanıcının seçtiği destek paketine göre e-posta gönder ve DB kaydı oluştur"""
    from .services.email_service import EmailService
    from .models import Donation

    try:
        data = json.loads(request.body)
        tier_id = data.get('tier_id')
        tier_name = data.get('tier_name')
        tier_amount = data.get('tier_amount')

        if not all([tier_id, tier_name, tier_amount]):
            return JsonResponse({'success': False, 'error': 'Geçersiz veri'}, status=400)

        tier = DonationTier.objects.filter(id=tier_id, is_active=True).first()
        if not tier:
            return JsonResponse({'success': False, 'error': 'Paket bulunamadı'}, status=404)

        user = request.user

        # Daha önce pending/pending_confirmation kaydı varsa yeniden kullan
        donation = Donation.objects.filter(
            user=user,
            status__in=['pending', 'pending_confirmation'],
        ).order_by('-created_at').first()

        if not donation:
            donation = Donation.objects.create(
                user=user,
                email=user.email,
                name=user.get_full_name() or user.username,
                amount=tier.min_amount,
                payment_id=f"IBAN-{uuid.uuid4().hex[:12].upper()}",
                conversation_id=f"TIER-{tier.pk}",
                status='pending',
            )

        confirm_url = request.build_absolute_uri(
            reverse('mark_donation_transferred', args=[donation.pk])
        )

        context = {
            'username': user.username,
            'tier_amount': tier_amount,
            'tier_name': tier_name,
            'premium_days': tier.premium_days,
            'confirm_url': confirm_url,
        }

        html_message = render_to_string('forum/emails/support_payment_details.html', context)
        plain_message = strip_tags(html_message)

        email_sent = EmailService._send_email(
            to_email=user.email,
            subject="Analizus Bağış İşlemi",
            html_content=html_message,
            plain_content=plain_message
        )

        if email_sent:
            return JsonResponse({
                'success': True,
                'message': 'E-posta gönderildi',
                'donation_id': donation.pk,
                'confirm_url': confirm_url,
            })
        else:
            return JsonResponse({'success': False, 'error': 'E-posta gönderilemedi'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Geçersiz JSON'}, status=400)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Beklenmeyen hata'}, status=500)


@login_required
def mark_donation_transferred(request, pk):
    """Kullanıcının havaleyi yaptığını bildirmesi."""
    from .models import Donation
    donation = get_object_or_404(Donation, pk=pk, user=request.user)

    if donation.status == 'completed':
        messages.info(request, "Bu bağışınız zaten onaylanmış.")
        return redirect('profile_detail', username=request.user.username)

    if donation.status == 'pending_confirmation':
        messages.info(request, "Bildiriminiz daha önce alındı. Onay bekleniyor.")
        return redirect('profile_detail', username=request.user.username)

    donation.status = 'pending_confirmation'
    donation.save(update_fields=['status'])

    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            sender=request.user,
            verb=f"'{donation.name or request.user.username}' kullanıcısı {donation.amount}₺ bağış havalesini yaptığını bildirdi.",
            target=None,
        )

    messages.success(request, "Bildiriminiz alındı. Havale kontrol edildikten sonra Premium üyeliğiniz aktifleştirilecektir.")
    return redirect('profile_detail', username=request.user.username)


def hangi_test(request):
    """İnteraktif istatistik testi karar ağacı — SEO sayfası."""
    return render(request, 'forum/hangi_test.html')


def uzman_dizini(request):
    """Uzman Dizini — iş kategorisi/puan bazlı filtrelenebilir analist listesi."""
    cat_id = request.GET.get('cat', '').strip()
    sort_by = request.GET.get('sort', 'puan')  # puan | is | aktif

    # Boş cat param → canonical URL'ye yönlendir (sort varsa koru)
    if 'cat' in request.GET and not cat_id:
        if sort_by and sort_by != 'puan':
            return redirect(f"{reverse('uzman_dizini')}?sort={sort_by}")
        return redirect('uzman_dizini')

    # Son forum yanıtı (subquery) — Post.created_by FK'sı, Topic.subject
    last_post_subq = Post.objects.filter(
        created_by=OuterRef('user'),
    ).order_by('-created_at').values('topic__subject')[:1]

    last_post_url_subq = Post.objects.filter(
        created_by=OuterRef('user'),
    ).order_by('-created_at').values('topic__pk')[:1]

    profiles = (
        Profile.objects
        .select_related('user')
        .prefetch_related('skills', 'badges')
        .filter(is_public=True)
        .filter(
            Q(rank__in=['contributor', 'expert', 'master', 'legend', 'admin'])
            | Q(skills__isnull=False)
            | Q(best_answers_count__gt=0)
        )
        .distinct()
        .annotate(
            completed_jobs=Count(
                'user__proposals',
                filter=Q(
                    user__proposals__status='accepted',
                    user__proposals__job__status='completed',
                ),
                distinct=True,
            ),
            avg_rating=Avg(
                'user__received_reviews__rating',
                filter=Q(user__received_reviews__is_approved=True),
            ),
            last_topic_title=Subquery(last_post_subq),
            last_topic_pk=Subquery(last_post_url_subq),
        )
    )

    if cat_id:
        profiles = profiles.filter(skills__id=cat_id)

    if sort_by == 'is':
        profiles = profiles.order_by('-completed_jobs', '-reputation')
    elif sort_by == 'aktif':
        profiles = profiles.order_by('-last_seen', '-reputation')
    else:
        profiles = profiles.order_by('-reputation', '-completed_jobs')

    job_categories = JobCategory.objects.filter(is_active=True).order_by('order', 'title')

    return render(request, 'forum/uzman_dizini.html', {
        'profiles': profiles,
        'job_categories': job_categories,
        'selected_cat': cat_id,
        'sort_by': sort_by,
    })


# ─── ÇALIŞMA ODALARI ─────────────────────────────────────────────────────────

STUDYROOM_MAX_DAYS = 90  # Her halükarda 3 ayı geçemez
STUDYROOM_MIN_DAYS = 7
STUDYROOM_MIN_POINTS = 200  # 200+ puan veya staff


def _studyroom_eligibility(user):
    """(can_create: bool, reason: str)"""
    if not user.is_authenticated:
        return False, 'Giriş yapmanız gerekiyor.'
    if not hasattr(user, 'profile'):
        return False, 'Profil bulunamadı.'
    if not user.profile.email_verified and not user.is_staff:
        return False, 'E-posta doğrulaması gereklidir.'
    if not user.is_staff:
        score = user.profile.total_score
        if score < STUDYROOM_MIN_POINTS:
            return False, f'Çalışma odası açmak için en az {STUDYROOM_MIN_POINTS} puan gereklidir. (Mevcut: {score})'
        active_own = StudyRoom.objects.filter(creator=user, status__in=['pending', 'active']).exists()
        if active_own:
            return False, 'Zaten aktif veya onay bekleyen bir çalışma odanız var. Aynı anda yalnızca 1 oda açabilirsiniz.'
    return True, ''


def studyroom_list(request):
    """Tüm aktif çalışma odaları listesi."""
    # Süresi dolanları arşivle
    for room in StudyRoom.objects.filter(status='active'):
        room.auto_archive_if_expired()

    category_slug = request.GET.get('kategori', '')
    status_filter = request.GET.get('durum', 'active')

    rooms = StudyRoom.objects.select_related('creator', 'category').prefetch_related('memberships')

    if status_filter == 'archived':
        rooms = rooms.filter(status='archived')
    elif status_filter == 'all' and (request.user.is_authenticated and request.user.is_staff):
        rooms = rooms.exclude(status='rejected')
    else:
        rooms = rooms.filter(status='active')

    if category_slug:
        rooms = rooms.filter(category__slug=category_slug)

    rooms = rooms.annotate(member_cnt=Count('memberships', distinct=True)).order_by('-created_at')

    categories = Category.objects.filter(study_rooms__status='active').distinct()
    can_create, reason = _studyroom_eligibility(request.user)

    return render(request, 'forum/studyroom_list.html', {
        'rooms': rooms,
        'categories': categories,
        'selected_category': category_slug,
        'status_filter': status_filter,
        'can_create': can_create,
        'ineligibility_reason': reason,
        'STUDYROOM_MIN_POINTS': STUDYROOM_MIN_POINTS,
    })


@login_required
def studyroom_create(request):
    """Çalışma odası açma formu — şartname onayı dahil."""
    can_create, reason = _studyroom_eligibility(request.user)
    if not can_create:
        messages.error(request, reason)
        return redirect('studyroom_list')

    from django.utils import timezone as tz

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        goal = request.POST.get('goal', '').strip()
        category_id = request.POST.get('category', '')
        ends_at_str = request.POST.get('ends_at', '')
        max_members = int(request.POST.get('max_members', 20))
        is_public = request.POST.get('is_public') == '1'
        terms_agreed = request.POST.get('terms_agreed') == '1'
        creator_bio = request.POST.get('creator_bio', '').strip()[:300]

        errors = []
        if len(title) < 10:
            errors.append('Başlık en az 10 karakter olmalıdır.')
        if len(description) < 50:
            errors.append('Açıklama en az 50 karakter olmalıdır.')
        if len(goal) < 20:
            errors.append('Hedef en az 20 karakter olmalıdır.')
        if not terms_agreed:
            errors.append('Şartnameyi onaylamanız zorunludur.')

        ends_at = None
        if ends_at_str:
            try:
                from datetime import datetime
                ends_at = tz.make_aware(datetime.strptime(ends_at_str, '%Y-%m-%d'))
                min_date = tz.now() + timedelta(days=STUDYROOM_MIN_DAYS)
                max_date = tz.now() + timedelta(days=STUDYROOM_MAX_DAYS)
                if ends_at < min_date:
                    errors.append(f'Bitiş tarihi en az {STUDYROOM_MIN_DAYS} gün sonrası olmalıdır.')
                if ends_at > max_date:
                    errors.append(f'Bitiş tarihi en fazla {STUDYROOM_MAX_DAYS} gün ({STUDYROOM_MAX_DAYS//30} ay) sonrası olabilir.')
            except ValueError:
                errors.append('Geçersiz tarih formatı.')
        else:
            errors.append('Bitiş tarihi zorunludur.')

        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        if not errors:
            # Staff ise direkt aktif, değilse onay bekliyor
            initial_status = 'active' if request.user.is_staff else 'pending'

            room = StudyRoom.objects.create(
                title=title,
                description=description,
                goal=goal,
                creator_bio=creator_bio,
                category=category,
                creator=request.user,
                ends_at=ends_at,
                max_members=max(5, min(max_members, 200)),
                is_public=is_public,
                status=initial_status,
                terms_agreed=True,
                terms_agreed_at=tz.now(),
            )
            # Kurucuyu üye olarak ekle
            StudyRoomMembership.objects.create(room=room, user=request.user, role='creator')

            # Admin bildirimi (staff değilse)
            if not request.user.is_staff:
                try:
                    from .email_utils import EmailService
                    admins = User.objects.filter(is_staff=True).values_list('email', flat=True)
                    for admin_email in admins:
                        if admin_email:
                            EmailService._send_email(
                                to_email=admin_email,
                                subject=f'[Analizus] Yeni Çalışma Odası Onay Talebi: {room.title}',
                                html_content=f'<p><strong>{request.user.username}</strong> tarafından yeni bir çalışma odası oluşturuldu.</p>'
                                             f'<p><strong>Başlık:</strong> {room.title}</p>'
                                             f'<p><strong>Hedef:</strong> {room.goal}</p>'
                                             f'<p>Admin panelinden inceleyebilirsiniz.</p>',
                                plain_content=f'{request.user.username} tarafından "{room.title}" odası oluşturuldu. Admin panelinden inceleyin.',
                            )
                except Exception:
                    pass

            if initial_status == 'active':
                messages.success(request, 'Çalışma odanız başarıyla açıldı!')
                return redirect('studyroom_detail', slug=room.slug)
            else:
                messages.success(request, 'Çalışma odanız oluşturuldu. Admin onayı bekleniyor.')
                return redirect('studyroom_list')

        categories = Category.objects.all().order_by('title')
        return render(request, 'forum/studyroom_create.html', {
            'terms': STUDYROOM_TERMS,
            'categories': categories,
            'errors': errors,
            'post': request.POST,
            'STUDYROOM_MAX_DAYS': STUDYROOM_MAX_DAYS,
            'STUDYROOM_MIN_DAYS': STUDYROOM_MIN_DAYS,
        })

    categories = Category.objects.all().order_by('title')
    from django.utils import timezone as tz
    default_end = (tz.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    max_end = (tz.now() + timedelta(days=STUDYROOM_MAX_DAYS)).strftime('%Y-%m-%d')
    min_end = (tz.now() + timedelta(days=STUDYROOM_MIN_DAYS)).strftime('%Y-%m-%d')

    return render(request, 'forum/studyroom_create.html', {
        'terms': STUDYROOM_TERMS,
        'categories': categories,
        'default_end': default_end,
        'max_end': max_end,
        'min_end': min_end,
        'STUDYROOM_MAX_DAYS': STUDYROOM_MAX_DAYS,
        'STUDYROOM_MIN_DAYS': STUDYROOM_MIN_DAYS,
    })


def studyroom_detail(request, slug):
    """Oda detay sayfası: gönderiler + üyeler."""
    room = get_object_or_404(StudyRoom, slug=slug)
    room.auto_archive_if_expired()

    if room.status == 'pending' and not (request.user.is_authenticated and
                                          (request.user.is_staff or room.creator == request.user)):
        raise Http404

    is_member = False
    membership = None
    if request.user.is_authenticated:
        membership = StudyRoomMembership.objects.filter(room=room, user=request.user).first()
        is_member = membership is not None

    # POST: yeni mesaj
    if request.method == 'POST' and request.user.is_authenticated:
        if room.status != 'active':
            return JsonResponse({'error': 'Oda aktif değil.'}, status=400)
        if not is_member:
            return JsonResponse({'error': 'Odaya katılmadan mesaj gönderemezsiniz.'}, status=403)

        message = request.POST.get('message', '').strip()
        file = request.FILES.get('file')

        if not message and not file:
            return JsonResponse({'error': 'Boş mesaj gönderilemez.'}, status=400)

        if file:
            if file.size > settings.MAX_UPLOAD_SIZE:
                return JsonResponse({'error': 'Dosya boyutu 5 MB\'ı geçemez.'}, status=400)
            if file.content_type not in settings.ALLOWED_ATTACHMENT_TYPES:
                return JsonResponse({'error': 'Bu dosya türü desteklenmiyor.'}, status=400)

        post = StudyRoomPost(room=room, author=request.user, message=message)
        if file:
            post.file = file
        post.save()

        # @mention bildirimleri
        import re as _re
        mentions = set(_re.findall(r'@(\w+)', message))
        if mentions:
            from .email_utils import notify_room_mention
            room_member_ids = set(room.memberships.values_list('user_id', flat=True))
            ct = ContentType.objects.get_for_model(StudyRoomPost)
            for mentioned_user in User.objects.filter(username__in=mentions).exclude(pk=request.user.pk):
                if mentioned_user.pk in room_member_ids:
                    Notification.objects.create(
                        recipient=mentioned_user,
                        sender=request.user,
                        verb=f"sizi '{room.title}' odasında etiketledi",
                        content_type=ct,
                        object_id=post.id,
                    )
                    notify_room_mention(request.user, mentioned_user, room, message)

        file_url = post.file.url if post.file else ''
        file_name = post.file.name.split('/')[-1] if post.file else ''
        file_type = 'image' if file and file.content_type.startswith('image/') else (
                    'pdf' if file and file.content_type == 'application/pdf' else
                    ('doc' if file else ''))

        return JsonResponse({
            'id': post.id,
            'author': request.user.username,
            'message': post.message,
            'created_at': timezone.localtime(post.created_at).isoformat(),
            'file_url': file_url,
            'file_name': file_name,
            'file_type': file_type,
        })

    posts = room.room_posts.select_related('author__profile').all() if is_member else []
    members = room.memberships.select_related('user__profile').all()

    return render(request, 'forum/studyroom_detail.html', {
        'room': room,
        'posts': posts,
        'members': members,
        'is_member': is_member,
        'membership': membership,
    })


@login_required
@require_POST
def studyroom_join(request, slug):
    """Odaya katıl / ayrıl."""
    room = get_object_or_404(StudyRoom, slug=slug, status='active')

    if room.is_expired:
        return JsonResponse({'error': 'Odanın süresi dolmuş.'}, status=400)

    membership = StudyRoomMembership.objects.filter(room=room, user=request.user).first()

    if membership:
        if membership.role == 'creator':
            return JsonResponse({'error': 'Kurucu odadan ayrılamaz.'}, status=400)
        membership.delete()
        return JsonResponse({'action': 'left', 'member_count': room.member_count})
    else:
        if not room.is_public:
            return JsonResponse({'error': 'Bu oda herkese açık değil.'}, status=403)
        if room.member_count >= room.max_members:
            return JsonResponse({'error': 'Oda kapasitesi doldu.'}, status=400)
        StudyRoomMembership.objects.create(room=room, user=request.user, role='member')
        return JsonResponse({'action': 'joined', 'member_count': room.member_count})


@login_required
@require_GET
def studyroom_poll(request, slug):
    """Oda mesaj polling: son ID'den sonraki yeni gönderileri döndür."""
    room = get_object_or_404(StudyRoom, slug=slug)
    after_id = int(request.GET.get('after', 0))
    new_posts = room.room_posts.filter(id__gt=after_id).select_related('author__profile').order_by('id')
    data = []
    for post in new_posts:
        file_url = post.file.url if post.file else ''
        file_name = post.file.name.split('/')[-1] if post.file else ''
        ct = post.file.name.rsplit('.', 1)[-1].lower() if post.file else ''
        file_type = 'image' if ct in ('jpg', 'jpeg', 'png', 'gif', 'webp') else (
                    'pdf' if ct == 'pdf' else ('doc' if file_url else ''))
        data.append({
            'id': post.id,
            'author': post.author.username,
            'message': post.message,
            'created_at': timezone.localtime(post.created_at).isoformat(),
            'is_own': post.author == request.user,
            'avatar_url': post.author.profile.avatar.url if post.author.profile.avatar else '',
            'file_url': file_url,
            'file_name': file_name,
            'file_type': file_type,
        })
    return JsonResponse({'posts': data})


@login_required
@require_POST
def studyroom_invite(request, slug):
    """Kurucu: odaya kullanıcı adıyla üye davet et."""
    room = get_object_or_404(StudyRoom, slug=slug)
    if room.status not in ('active', 'pending'):
        return JsonResponse({'error': 'Oda bu durumda davet kabul etmiyor.'}, status=400)
    if not StudyRoomMembership.objects.filter(room=room, user=request.user, role='creator').exists():
        return JsonResponse({'error': 'Yalnızca kurucu üye davet edebilir.'}, status=403)

    username = request.POST.get('username', '').strip()
    try:
        invited_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error': f'"{username}" kullanıcısı bulunamadı.'}, status=404)

    if StudyRoomMembership.objects.filter(room=room, user=invited_user).exists():
        return JsonResponse({'error': 'Bu kullanıcı zaten odada.'}, status=400)

    if room.member_count >= room.max_members:
        return JsonResponse({'error': 'Oda kapasitesi doldu.'}, status=400)

    StudyRoomMembership.objects.create(room=room, user=invited_user, role='member')

    ct = ContentType.objects.get_for_model(StudyRoom)
    Notification.objects.create(
        recipient=invited_user,
        sender=request.user,
        verb=f"sizi '{room.title}' çalışma odasına davet etti",
        content_type=ct,
        object_id=room.id,
    )

    return JsonResponse({
        'success': True,
        'username': invited_user.username,
        'member_count': room.member_count,
    })


@login_required
def studyroom_edit(request, slug):
    """Kurucu: oda ayarlarını düzenle."""
    room = get_object_or_404(StudyRoom, slug=slug)
    if room.creator != request.user:
        raise Http404
    if room.status == 'archived':
        return redirect('studyroom_detail', slug=slug)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        goal = request.POST.get('goal', '').strip()
        is_public = request.POST.get('is_public') == 'on'

        if title:
            room.title = title
        if description:
            room.description = description
        if goal:
            room.goal = goal
        room.is_public = is_public
        room.save(update_fields=['title', 'description', 'goal', 'is_public'])
        return redirect('studyroom_detail', slug=room.slug)

    return render(request, 'forum/studyroom_edit.html', {'room': room})


@login_required
@require_POST
def studyroom_delete(request, slug):
    """Kurucu: odayı sil (yalnızca pending/rejected durumlarda)."""
    room = get_object_or_404(StudyRoom, slug=slug)
    if room.creator != request.user:
        return JsonResponse({'error': 'Yetki yok.'}, status=403)
    if room.status == 'active':
        return JsonResponse({'error': 'Aktif oda silinemez. Önce admin ile iletişime geçin.'}, status=400)
    room.delete()
    return JsonResponse({'success': True, 'redirect': '/odalar/'})


@login_required
@require_POST
def studyroom_approve(request, slug):
    """Admin: odayı onayla veya reddet."""
    if not request.user.is_staff:
        raise Http404
    room = get_object_or_404(StudyRoom, slug=slug)
    action = request.POST.get('action')
    note = request.POST.get('note', '')

    if action == 'approve':
        room.status = 'active'
    elif action == 'reject':
        room.status = 'rejected'
    room.reviewed_by = request.user
    room.review_note = note
    room.save(update_fields=['status', 'reviewed_by', 'review_note'])
    return JsonResponse({'status': room.status})


@login_required
def onboarding(request):
    profile = request.user.profile

    if profile.onboarding_completed:
        return redirect('home')

    if request.method == 'POST':
        if 'skip' in request.POST:
            profile.onboarding_completed = True
            profile.save(update_fields=['onboarding_completed'])
            return redirect('home')

        segment = request.POST.get('segment', '')

        if segment:
            profile.segment = segment
        profile.onboarding_completed = True
        profile.save(update_fields=['segment', 'onboarding_completed'])

        messages.success(request, 'Hoş geldiniz!')
        return redirect('home')

    segment_choices = Profile.SEGMENT_CHOICES
    capability_info = [
        ('📊', 'İstatistik Analizi', 'SPSS, R, Python, AMOS, SmartPLS ile profesyonel istatistik analizleri'),
        ('🔎', 'Veri Kazıma & Toplama', 'Anket, web ve akademik veritabanlarından veri toplama desteği'),
        ('🧑‍🏫', 'Danışmanlık', 'Alanında uzman akademisyen ve danışmanlarla Pazaryeri üzerinden eşleşin'),
        ('📁', 'Proje Desteği', 'Tez, makale ve kurumsal projeleriniz için uçtan uca destek'),
        ('🎓', 'Akademik Destek', 'Tez ve makale yazım sürecinde yöntem ve rehberlik desteği'),
        ('📈', 'Bibliometrik Analiz', 'Atıf ve yayın verileriyle bibliometrik analiz yaptırın'),
        ('🔍', 'Literatür / Akademik Tarama', 'YÖK Tez, TR Dizin ve uluslararası veritabanlarında tarama'),
        ('💬', 'Forumda Soru-Cevap', 'Merak ettiklerinizi sorun, bilgi birikiminizi toplulukla paylaşın'),
    ]
    tool_names = ['SPSS', 'R', 'Python', 'Excel', 'SmartPLS', 'AMOS', 'Stata', 'NVivo', 'MAXQDA', 'AI Araçları', 'Akademik Danışmanlık']
    return render(request, 'forum/onboarding.html', {
        'segment_choices': segment_choices,
        'capability_info': capability_info,
        'tool_names': tool_names,
    })


def tarama_hub(request):
    tools = [
        {
            'title': 'YÖK Tez Kazıma ve İndirme Aracı',
            'desc': 'Anahtar kelime, yazar veya danışmanla arama yapın; tez verilerini Excel veya TXT olarak indirin.',
            'icon': 'bi-mortarboard-fill',
            'color': 'success',
            'url_name': 'yoktez:landing',
            'feature_key': 'yoktez',
        },
        {
            'title': 'OpenAlex Yayın Kazıma',
            'desc': '240 milyondan fazla akademik yayından kodsuz veri kazıma. Başlık, yazar, kurum ve atıf bilgileri.',
            'icon': 'bi-search',
            'color': 'primary',
            'url_name': 'openalex:landing',
            'feature_key': 'openalex',
        },
        {
            'title': 'TR Dizin Makale Kazıma',
            'desc': 'TR Dizin\'den anahtar kelime ile makale arayın; yazarları, dergileri ve atıf bilgilerini indirin.',
            'icon': 'bi-journal-text',
            'color': 'primary',
            'url_name': 'trdizin:landing',
            'feature_key': 'trdizin',
        },
        {
            'title': 'Semantic Scholar Yayın Kazıma',
            'desc': '200 milyondan fazla akademik yayın arasında kodsuz arama yapın. WoS, Scopus ve arXiv dahil tüm büyük veri tabanlarını kapsar.',
            'icon': 'bi-diagram-3-fill',
            'color': 'info',
            'url_name': 'semanticscholar:landing',
            'feature_key': 'semanticscholar',
        },
        {
            'title': 'Üniversite Tez Arşivi',
            'desc': '19 Türk üniversitesinin açık erişim arşivinde anahtar kelime ile tez ve makale arayın.',
            'icon': 'bi-mortarboard',
            'color': 'warning',
            'url_name': 'oaipmh:landing',
            'feature_key': 'oaipmh',
        },
    ]
    settings = SiteSettings.load()
    tools = [t for t in tools if getattr(settings, f'feature_{t["feature_key"]}', True)]
    return render(request, 'tarama_hub.html', {'tools': tools})


# ─────────────────────────────────────────────────────────────
# REFERRAL (DAVET) SİSTEMİ
# ─────────────────────────────────────────────────────────────

def referral_landing(request, code):
    """Davet linki: session'a kodu yaz, kayıt sayfasına yönlendir."""
    if request.user.is_authenticated:
        messages.info(request, 'Zaten giriş yaptınız. Davet sistemi yalnızca yeni kayıtlar için geçerlidir.')
        return redirect('home')
    try:
        ReferralCode.objects.get(code=code)
        request.session['ref_code'] = code
        messages.success(request, 'Davet bağlantısıyla geldiniz! Kayıt olarak platforma katılın.')
    except ReferralCode.DoesNotExist:
        messages.warning(request, 'Geçersiz davet bağlantısı.')
    return redirect('register')


@login_required
def referral_dashboard(request):
    """Kullanıcının davet istatistikleri ve linki."""
    referral_code = ReferralCode.get_or_create_for_user(request.user)
    referrals = ReferralUse.objects.filter(
        referrer=request.user
    ).select_related('referred').order_by('-created_at')

    total = referrals.count()
    qualified = referrals.filter(rewarded=True).count()
    pending = referrals.filter(rewarded=False, flagged=False).count()
    total_premium_days = referrals.filter(rewarded=True).aggregate(
        s=models.Sum('premium_days_awarded')
    )['s'] or 0
    total_reputation = referrals.filter(rewarded=True).aggregate(
        s=models.Sum('reputation_awarded')
    )['s'] or 0

    # Rozet ilerleme: hangi eşiklere ulaşıldı / ne kadar kaldı
    milestones = [
        {'count': 1,  'slug': 'davetci',         'label': 'Davetçi',        'icon': 'bi-person-plus',  'color': '#22c55e'},
        {'count': 5,  'slug': 'topluluk-elcisi', 'label': 'Topluluk Elçisi','icon': 'bi-people-fill',  'color': '#a855f7'},
        {'count': 10, 'slug': 'buyukelci',        'label': 'Büyükelçi',      'icon': 'bi-award-fill',   'color': '#eab308'},
    ]
    for m in milestones:
        m['earned'] = qualified >= m['count']
        m['remaining'] = max(0, m['count'] - qualified)

    referral_url = request.build_absolute_uri(f'/davet/{referral_code.code}/')

    context = {
        'referral_code': referral_code,
        'referral_url': referral_url,
        'referrals': referrals,
        'total': total,
        'qualified': qualified,
        'pending': pending,
        'total_premium_days': total_premium_days,
        'total_reputation': total_reputation,
        'milestones': milestones,
    }
    return render(request, 'forum/referral_dashboard.html', context)
