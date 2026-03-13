from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta
import uuid
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import Section, Category, Topic, Post, Profile, PrivateMessage, PostLike, Notification, EmailVerification, DailyTip, QuizQuestion, QuizScore, SuccessStory, FreelanceJob, JobProposal, JobReview, Skill, Badge, UserQuizAttempt, JobPayment, SiteSettings, BlogCategory, BlogPost, DonationTier, StudyRoom, StudyRoomMembership, StudyRoomPost, STUDYROOM_TERMS
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
    sections_data = []
    for section in sections:
        cats = [c for c in categories_qs if c.section_id == section.pk]
        for c in cats:
            c.is_popular = c.slug in top_slugs
            # Son aktivite sadece 30 gün içindeyse göster
            c.show_last_activity = (
                c.last_post_at is not None and c.last_post_at >= cutoff
            )
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


# --- ANA SAYFA ---
def home(request):
    sections = Section.objects.all().order_by('order')

    # Widget verileri
    # İstatistikler
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    completed_jobs = FreelanceJob.objects.filter(status='completed').count()

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
        # Widgetlar
        'recent_topics': recent_topics,
        'popular_topics': popular_topics,
        'daily_tip': daily_tip,
        'quiz_question': quiz_question,
        'donation_tiers': donation_tiers,
        'featured_story': featured_story,
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
    # Süresi dolan açık ilanları otomatik kapat
    from django.utils import timezone as tz
    from datetime import timedelta
    now = tz.now()
    FreelanceJob.objects.filter(status='open', expires_at__lt=now).update(status='cancelled')
    FreelanceJob.objects.filter(status='open', expires_at__isnull=True, created_at__lt=now - timedelta(days=30)).update(status='cancelled')

    sort = request.GET.get('sort', 'newest')
    jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category').annotate(
        p_count=Count('proposals', distinct=True)
    )

    if sort == 'views':
        jobs = jobs.order_by('-views', '-created_at')
    elif sort == 'proposals':
        jobs = jobs.order_by('-p_count', '-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    # Yetki bilgileri
    can_post = FreelanceJob.can_post(request.user)
    can_post_reason = ""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        _, can_post_reason = request.user.profile.can_post_job()

    return render(request, 'forum/market/job_list.html', {
        'jobs': jobs,
        'current_sort': sort,
        'can_post': can_post,
        'can_post_reason': can_post_reason,
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
    return render(request, 'forum/market/post_job.html', {'form': form})

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
        job.status = 'cancelled'
        job.save()
        messages.success(request, 'İlanınız başarıyla kapatılmıştır.')
    else:
        messages.warning(request, 'Bu ilan zaten kapalı veya işlemde.')

    return redirect('job_detail', pk=pk)


@login_required
@require_POST
def accept_proposal(request, pk, proposal_id):
    """Teklifi kabul et, ilanı askıya al"""
    job = get_object_or_404(FreelanceJob, pk=pk, owner=request.user)
    proposal = get_object_or_404(JobProposal, pk=proposal_id, job=job)

    if job.status != 'open':
        messages.warning(request, 'Bu ilan artık aktif değil.')
        return redirect('job_detail', pk=pk)

    # Teklifi kabul et
    proposal.status = 'accepted'
    proposal.save()

    # Diğer teklifleri reddet
    job.proposals.exclude(pk=proposal_id).update(status='rejected')

    # İlanı askıya al
    job.status = 'in_progress'
    job.save()

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
@login_required
def job_detail(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)

    # Süresi geçmişse otomatik kapat
    job.expire_if_needed()

    # Görüntülenme sayısını artır
    job.views += 1
    job.save()

    user_proposal = None
    proposal_form = None

    # Teklif verme yetkisi kontrolü
    is_expert = JobProposal.can_propose(request.user)
    can_propose_reason = ""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        _, can_propose_reason = request.user.profile.can_propose()

    # 1. Teklifleri görme yetkisi (İlan sahibi veya Admin)
    if request.user == job.owner or request.user.is_superuser or request.user.is_staff:
        proposals = job.proposals.select_related('expert', 'expert__profile').all()
    else:
        proposals = None

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
    accepted_proposal = job.proposals.filter(status='accepted').first()
    if request.user.is_authenticated and accepted_proposal:
        # İlan sahibi veya kabul edilen uzman mı?
        is_owner = request.user == job.owner
        is_expert_accepted = request.user == accepted_proposal.expert
        if (is_owner or is_expert_accepted) and job.status == 'in_progress':
            # Daha önce review yapmış mı?
            has_reviewed = job.reviews.filter(reviewer=request.user).exists()
            can_review = not has_reviewed

    return render(request, 'forum/market/job_detail.html', {
        'job': job,
        'proposals': proposals,
        'user_proposal': user_proposal,
        'proposal_form': proposal_form,
        'is_liked': is_liked,
        'is_saved': is_saved,
        'is_expert': is_expert,
        'can_propose_reason': can_propose_reason,
        'similar_jobs': similar_jobs,
        'reviews': reviews,
        'can_review': can_review,
        'accepted_proposal': accepted_proposal
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
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
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

            login(request, user)
            return redirect('verification_pending')
    else:
        form = RegisterForm()
    return render(request, 'forum/register.html', {'form': form})


# --- GİRİŞ (Rate Limited) ---
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key='post:username', rate='5/m', method='POST', block=True)
def custom_login(request):
    """Rate limited login view"""
    from django.contrib.auth import authenticate, login as auth_login
    from django.contrib.auth.forms import AuthenticationForm
    from django.utils import timezone
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
    all_skills = Skill.objects.all()

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

        # Yetenekler (Skills)
        selected_skills = request.POST.getlist('skills')

        # Kullanıcının eklediği özel yetenekler (Virgülle ayrılmış)
        custom_skills = request.POST.get('custom_skills')
        if custom_skills:
            for skill_name in custom_skills.split(','):
                skill_name = skill_name.strip()
                if skill_name:
                    # Varsa getir (case-insensitive), yoksa oluştur
                    skill = Skill.objects.filter(name__iexact=skill_name).first()
                    if not skill:
                        skill = Skill.objects.create(name=skill_name)
                    selected_skills.append(str(skill.id))

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
        messages.info(request, "Bilgileriniz KVKK kapsamında 3. kişilerle paylaşılmamaktadır.")
        return redirect('profile_edit')
    
    return render(request, 'forum/profile_edit.html', {'user': user, 'profile': profile, 'all_skills': all_skills})

# --- GELEN KUTUSU ---
@feature_required('messaging')
@login_required
def inbox(request):
    # Sayfa görüntülendiğinde tüm okunmamış mesajları okundu yap
    PrivateMessage.objects.filter(receiver=request.user, is_read=False).update(is_read=True)

    received_messages = PrivateMessage.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'forum/inbox.html', {'received_messages': received_messages})


# --- MESAJ POLLING API ---
@login_required
@require_GET
def api_chat_poll(request, username):
    """Chat sayfası için polling: son mesaj ID'sinden sonraki yeni mesajları döndür"""
    after_id = int(request.GET.get('after', 0))
    receiver = get_object_or_404(User, username=username)

    new_messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user),
        id__gt=after_id
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
            'timestamp': msg.created_at.strftime('%H:%M'),
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
            'created_at': msg.created_at.strftime('%d %b %Y - %H:%M'),
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
                messages.error(request, 'Bu dosya türü desteklenmiyor. (Resim, PDF, Word, Excel, PowerPoint)')
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

    return render(request, 'forum/send_message.html', {'receiver': receiver, 'chat_messages': chat_messages})

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

    # GİZLİLİK KONTROLÜ: E-posta gösterimi
    # Eğer görüntüleyen kişi profil sahibi değilse ve kullanıcı e-postasını gizlemişse
    if request.user != profile_user and hasattr(profile_user, 'profile') and not profile_user.profile.show_email:
        profile_user.email = ""  # E-postayı gizle

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
    ).order_by('-created_at')[:20]
    given_proposals = JobProposal.objects.filter(expert=profile_user).select_related('job').order_by('-created_at')[:20]
    received_reviews = JobReview.objects.filter(reviewed_user=profile_user, is_approved=True).select_related('reviewer', 'job').order_by('-created_at')[:20]

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
        'posted_jobs': posted_jobs,
        'given_proposals': given_proposals,
        'received_reviews': received_reviews,
        'rating_stats': rating_stats,
        'quiz_stats': quiz_stats,
        'user_score': user_score,
        'quiz_rank': quiz_rank,
        'permissions': permissions,
        'next_badge': next_badge,
        'all_badges': all_badges,
        'user_badge_ids': user_badge_ids,
    })

# --- DİĞER ---
def about(request):
    return render(request, 'forum/about.html')

def how_it_works(request):
    """Nasıl Çalışır? sayfası"""
    return render(request, 'forum/how_it_works.html')

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
        return redirect('about')
    return redirect('about')

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
            'created_at': notif.created_at.strftime('%d.%m.%Y %H:%M'),
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


# --- AI ASISTAN ---
@feature_required('ai_assistant')
@login_required
def ai_assistant(request):
    """AI Asistan sayfası"""
    from .services.ai_service import groq_service
    from django.core.cache import cache

    # Kullanıcının günlük kullanım limiti
    cache_key = f"ai_usage_{request.user.id}_{timezone.now().date()}"
    usage_count = cache.get(cache_key, 0)
    daily_limit = 10  # Günlük 10 soru hakkı

    context = {
        'usage_count': usage_count,
        'daily_limit': daily_limit,
        'remaining': max(0, daily_limit - usage_count),
        'ai_available': groq_service.is_available(),
    }

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            messages.error(request, 'Lütfen bir soru girin.')
            return render(request, 'forum/ai_assistant.html', context)

        if usage_count >= daily_limit:
            messages.warning(request, f'Günlük {daily_limit} soru limitinizi doldurdunuz. Yarın tekrar deneyin.')
            return render(request, 'forum/ai_assistant.html', context)

        if not groq_service.is_available():
            messages.error(request, 'AI servisi şu anda kullanılamıyor.')
            return render(request, 'forum/ai_assistant.html', context)

        # AI'dan yanıt al
        result = groq_service.generate_response(user_message)

        if result['success']:
            # Kullanım sayısını artır (24 saat cache)
            cache.set(cache_key, usage_count + 1, 60 * 60 * 24)
            context['ai_response'] = result['response']
            context['user_question'] = user_message
            context['usage_count'] = usage_count + 1
            context['remaining'] = max(0, daily_limit - usage_count - 1)
        else:
            messages.error(request, result['error'])

    return render(request, 'forum/ai_assistant.html', context)


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

    # Token'ı kullanılmış olarak işaretle
    verification.is_used = True
    verification.save()

    # Hoş geldin e-postası gönder
    EmailService.send_welcome_email(user)

    messages.success(request, 'E-posta adresiniz başarıyla doğrulandı! Hoş geldiniz.')

    # Kullanıcı giriş yapmamışsa giriş yap
    if not request.user.is_authenticated:
        login(request, user)

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


# --- API: QUIZ & STORIES ---
@login_required
def api_get_quiz_question(request):
    """
    Kullanıcıya o gün cevaplamadığı rastgele bir quiz sorusu getirir.
    Günlük 20 soru limiti vardır.
    """
    try:
        today = timezone.now().date()

        # Kullanıcının bugün cevapladığı soruların ID'lerini al
        answered_today_ids = UserQuizAttempt.objects.filter(
            user=request.user,
            created_at__date=today
        ).values_list('question_id', flat=True)

        # Günlük limiti kontrol et
        if answered_today_ids.count() >= 20:
            return JsonResponse({'success': False, 'error': 'Günlük 20 soru limitinizi doldurdunuz. Yarın tekrar bekleriz!'})

        # Bugün cevaplanmamış, rastgele bir aktif soru getir
        question = QuizQuestion.objects.filter(is_active=True).exclude(id__in=answered_today_ids).order_by('?').first()

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
            # Neden soru bulunamadığını kontrol et
            if QuizQuestion.objects.filter(is_active=True).exists():
                # Sorular var ama hepsi bugün cevaplanmış
                return JsonResponse({'success': False, 'error': 'Bugünlük çözülecek soru kalmadı. Yarın tekrar bekleriz!'})
            else:
                # Veritabanında hiç aktif soru yok
                return JsonResponse({'success': False, 'error': 'Sistemde henüz aktif bir soru bulunmuyor.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Bir hata oluştu: {str(e)}'})

@login_required
def api_submit_quiz_answer(request):
    """Quiz cevabını kontrol eder ve puan/rozet verir"""
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


            return JsonResponse({
                'success': True,
                'is_correct': is_correct,
                'correct_answer': question.correct_answer,
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
            'date': d.completed_at.strftime('%d.%m.%Y') if d.completed_at else '',
        })

    return JsonResponse({
        'total': float(total),
        'recent_donors': donors_data,
        'donor_count': Donation.objects.filter(status='completed').count(),
    })


@require_POST
def create_donation(request):
    """iyzico ödeme formu oluşturur"""
    from django.conf import settings
    import iyzipay

    try:
        # API anahtarları kontrol et
        if not settings.IYZICO_API_KEY or not settings.IYZICO_SECRET_KEY:
            return JsonResponse({
                'success': False,
                'error': 'Ödeme sistemi henüz yapılandırılmadı. Lütfen daha sonra tekrar deneyin.'
            })

        data = json.loads(request.body)
        amount = data.get('amount')
        email = data.get('email', '')
        name = data.get('name', '')
        is_anonymous = data.get('is_anonymous', False)

        if not amount or float(amount) < 5:
            return JsonResponse({'success': False, 'error': 'Minimum bağış miktarı 5 TL\'dir.'})

        # Giriş yapmış kullanıcı varsa bilgilerini al
        user = request.user if request.user.is_authenticated else None
        if user and not email:
            email = user.email
        if user and not name:
            name = user.get_full_name() or user.username

        if not email:
            return JsonResponse({'success': False, 'error': 'E-posta adresi gereklidir.'})

        # Benzersiz ID'ler oluştur
        conversation_id = str(uuid.uuid4())[:20]
        payment_id = f"DON-{uuid.uuid4().hex[:12].upper()}"

        # Donation kaydı oluştur (pending)
        donation = Donation.objects.create(
            user=user,
            email=email,
            name=name,
            amount=amount,
            payment_id=payment_id,
            conversation_id=conversation_id,
            is_anonymous=is_anonymous,
            status='pending'
        )

        # iyzico ayarları
        import iyzipay
        options = {
            'api_key': getattr(settings, 'IYZICO_API_KEY', ''),
            'secret_key': getattr(settings, 'IYZICO_SECRET_KEY', ''),
            'base_url': getattr(settings, 'IYZICO_BASE_URL', 'sandbox-api.iyzipay.com')
        }

        # Callback URL
        callback_url = request.build_absolute_uri('/api/donation/callback/')

        # iyzico istek objesi
        checkout_form_request = {
            'locale': 'tr',
            'conversationId': conversation_id,
            'price': str(amount),
            'paidPrice': str(amount),
            'currency': 'TRY',
            'basketId': payment_id,
            'paymentGroup': 'PRODUCT',
            'callbackUrl': callback_url,
            'enabledInstallments': ['1'],
            'buyer': {
                'id': str(user.id) if user else 'GUEST',
                'name': name.split()[0] if name else 'Misafir',
                'surname': name.split()[-1] if name and len(name.split()) > 1 else 'Bağışçı',
                'gsmNumber': '+905000000000',
                'email': email,
                'identityNumber': '11111111111',
                'registrationAddress': 'Türkiye',
                'ip': get_client_ip(request),
                'city': 'Istanbul',
                'country': 'Turkey',
            },
            'shippingAddress': {
                'contactName': name or 'Bağışçı',
                'city': 'Istanbul',
                'country': 'Turkey',
                'address': 'Türkiye',
            },
            'billingAddress': {
                'contactName': name or 'Bağışçı',
                'city': 'Istanbul',
                'country': 'Turkey',
                'address': 'Türkiye',
            },
            'basketItems': [
                {
                    'id': payment_id,
                    'name': 'Analizus Bağış',
                    'category1': 'Bağış',
                    'itemType': 'VIRTUAL',
                    'price': str(amount),
                }
            ]
        }

        # iyzico checkout form oluştur
        logger.debug(f"[IYZICO] API Key: {settings.IYZICO_API_KEY[:20]}...")
        logger.debug(f"[IYZICO] Base URL: {settings.IYZICO_BASE_URL}")
        logger.debug(f"[IYZICO] Request: {checkout_form_request}")

        checkout_form = iyzipay.CheckoutFormInitialize().create(checkout_form_request, options)
        result = checkout_form.read().decode('utf-8')
        logger.debug(f"[IYZICO] Response: {result[:500]}")

        result_json = json.loads(result)

        if result_json.get('status') == 'success':
            return JsonResponse({
                'success': True,
                'checkoutFormContent': result_json.get('checkoutFormContent'),
                'token': result_json.get('token'),
                'payment_id': payment_id,
            })
        else:
            donation.status = 'failed'
            donation.save()
            error_msg = result_json.get('errorMessage', 'Ödeme formu oluşturulamadı.')
            logger.error(f"[IYZICO] Error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': error_msg
            })

    except Exception as e:
        import traceback
        logger.error(f"[IYZICO] Exception: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)})


def send_donation_thank_you_email(donation):
    """Bağış sonrası teşekkür e-postası gönderir (Django Mail)"""
    from .services.email_service import EmailService

    if not EmailService.is_configured():
        logger.warning(f"[DONATION] E-posta ayarları yapılmamış! Email gönderilemedi: {donation.email}")
        return

    premium_days = donation.get_premium_days()
    donor_name = donation.name or (donation.user.username if donation.user else "Değerli Bağışçımız")

    subject = f"Teşekkürler! {int(donation.amount)} TL Bağışınız İçin"

    # HTML içeriğini bir template'den render etmek en iyisidir, ama burada inline olarak bırakıyorum.
    # Gerçek bir projede, bu HTML'i 'forum/emails/donation_thank_you.html' gibi bir dosyaya taşıyın.
    context = {
        'donor_name': donor_name,
        'amount': int(donation.amount),
        'premium_days': premium_days,
    }
    html_message = render_to_string('forum/emails/donation_thank_you.html', context)
    plain_message = strip_tags(html_message)

    try:
        EmailService._send_email(
            to_email=donation.email,
            subject=subject,
            html_content=html_message,
            plain_content=plain_message
        )
        logger.info(f"[DONATION] Teşekkür e-postası gönderildi: {donation.email}")
    except Exception as e:
        logger.error(f"[DONATION] E-posta gönderilemedi: {e}")


def get_client_ip(request):
    """İstemci IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def donation_callback(request):
    """iyzico ödeme callback'i"""
    from django.conf import settings
    import iyzipay

    if request.method == 'POST':
        token = request.POST.get('token')

        if not token:
            return redirect('home')

        options = {
            'api_key': getattr(settings, 'IYZICO_API_KEY', ''),
            'secret_key': getattr(settings, 'IYZICO_SECRET_KEY', ''),
            'base_url': getattr(settings, 'IYZICO_BASE_URL', 'sandbox-api.iyzipay.com')
        }

        # Ödeme sonucunu sorgula
        checkout_form_result = iyzipay.CheckoutForm().retrieve({
            'locale': 'tr',
            'token': token,
        }, options)

        result = checkout_form_result.read().decode('utf-8')
        result_json = json.loads(result)

        basket_id = result_json.get('basketId')

        try:
            donation = Donation.objects.get(payment_id=basket_id)

            if result_json.get('status') == 'success' and result_json.get('paymentStatus') == 'SUCCESS':
                donation.status = 'completed'
                donation.completed_at = timezone.now()
                donation.save()

                # Premium üyelik ver
                donation.grant_premium()

                # Destekçi rozeti ver
                donation.grant_supporter_badge()

                # Teşekkür e-postası gönder
                send_donation_thank_you_email(donation)

                return redirect(f'/donation/success/?payment_id={donation.payment_id}')
            else:
                donation.status = 'failed'
                donation.save()
                messages.error(request, 'Ödeme işlemi başarısız oldu.')
                return redirect('home')

        except Donation.DoesNotExist:
            messages.error(request, 'Bağış kaydı bulunamadı.')
            return redirect('home')

    return redirect('home')


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

@csrf_exempt
def job_payment_callback(request):
    """İlan ödemesi callback"""
    from django.conf import settings
    import iyzipay

    if request.method == 'POST':
        token = request.POST.get('token')
        if not token:
            return redirect('home')

        options = {
            'api_key': getattr(settings, 'IYZICO_API_KEY', ''),
            'secret_key': getattr(settings, 'IYZICO_SECRET_KEY', ''),
            'base_url': getattr(settings, 'IYZICO_BASE_URL', 'sandbox-api.iyzipay.com')
        }

        checkout_form_result = iyzipay.CheckoutForm().retrieve({'locale': 'tr', 'token': token}, options)
        result = json.loads(checkout_form_result.read().decode('utf-8'))
        basket_id = result.get('basketId')

        try:
            payment = JobPayment.objects.get(payment_id=basket_id)
            
            if result.get('status') == 'success' and result.get('paymentStatus') == 'SUCCESS':
                payment.status = 'success'
                payment.save()

                # İlanı güncelle
                job = payment.job
                job.is_featured = True
                # Mevcut süre varsa üstüne ekle, yoksa şimdiden başlat
                now = timezone.now()
                start_time = job.featured_until if job.featured_until and job.featured_until > now else now
                job.featured_until = start_time + timedelta(days=7)
                job.save()

                messages.success(request, 'Ödeme başarılı! İlanınız vitrine taşındı.')
                return redirect('job_detail', pk=job.pk)
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, 'Ödeme başarısız oldu.')
        except JobPayment.DoesNotExist:
            messages.error(request, 'Ödeme kaydı bulunamadı.')

    return redirect('home')


# ═══════════════════════════════════════════════════════════════════════════════
# BLOG SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════════

@feature_required('blog')
def blog_list(request):
    """Blog ana sayfası - yazı listesi"""
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')

    # Kategori filtresi
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Öne çıkan yazılar
    featured_posts = posts.filter(is_featured=True)[:3]

    # Kategoriler
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)

    # Popüler yazılar
    popular_posts = posts.order_by('-views')[:5]

    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'popular_posts': popular_posts,
        'current_category': category_slug,
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

    # İlgili yazılar (aynı kategoriden)
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk)[:3]

    context = {
        'post': post,
        'is_liked': is_liked,
        'related_posts': related_posts,
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
    """Kullanıcının seçtiği destek paketine göre e-posta gönder"""
    from .services.email_service import EmailService

    try:
        # Request'ten veri al
        data = json.loads(request.body)
        tier_id = data.get('tier_id')
        tier_name = data.get('tier_name')
        tier_amount = data.get('tier_amount')

        # Validation
        if not all([tier_id, tier_name, tier_amount]):
            return JsonResponse({'success': False, 'error': 'Geçersiz veri'}, status=400)

        # Tier'ı veritabanından kontrol et
        tier = DonationTier.objects.filter(id=tier_id, is_active=True).first()
        if not tier:
            return JsonResponse({'success': False, 'error': 'Paket bulunamadı'}, status=404)

        user = request.user
        user_email = user.email
        username = user.username

        # E-posta metni
        email_subject = "Analizus Bağış İşlemi"
        
        context = {
            'username': username,
            'tier_amount': tier_amount,
            'tier_name': tier_name,
            'premium_days': tier.premium_days,
        }
        
        html_message = render_to_string('forum/emails/support_payment_details.html', context)
        plain_message = strip_tags(html_message)
        
        # Django Mail ile gönder
        email_sent = EmailService._send_email(
            to_email=user_email,
            subject=email_subject,
            html_content=html_message,
            plain_content=plain_message
        )

        if email_sent:
            return JsonResponse({'success': True, 'message': 'E-posta gönderildi'})
        else:
            return JsonResponse({'success': False, 'error': 'E-posta gönderilemedi'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Geçersiz JSON'}, status=400)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Beklenmeyen hata'}, status=500)


def hangi_test(request):
    """İnteraktif istatistik testi karar ağacı — SEO sayfası."""
    return render(request, 'forum/hangi_test.html')


def uzman_dizini(request):
    """Uzman Dizini — skill/rozet/puan bazlı filtrelenebilir analist listesi."""
    skill_slug = request.GET.get('skill', '').strip()
    sort_by = request.GET.get('sort', 'puan')  # puan | is | aktif

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

    if skill_slug:
        profiles = profiles.filter(skills__slug=skill_slug)

    if sort_by == 'is':
        profiles = profiles.order_by('-completed_jobs', '-reputation')
    elif sort_by == 'aktif':
        profiles = profiles.order_by('-last_seen', '-reputation')
    else:
        profiles = profiles.order_by('-reputation', '-completed_jobs')

    skills = Skill.objects.all().order_by('name')

    return render(request, 'forum/uzman_dizini.html', {
        'profiles': profiles,
        'skills': skills,
        'selected_skill': skill_slug,
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
        if not message:
            return JsonResponse({'error': 'Boş mesaj gönderilemez.'}, status=400)

        post = StudyRoomPost.objects.create(room=room, author=request.user, message=message)
        return JsonResponse({
            'id': post.id,
            'author': request.user.username,
            'message': post.message,
            'created_at': post.created_at.strftime('%d.%m.%Y %H:%M'),
        })

    posts = room.room_posts.select_related('author__profile').all()
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
