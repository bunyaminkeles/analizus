from django.shortcuts import render, redirect, get_object_or_404
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
from django.db.models import Count, Sum, Q, Avg
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta
import uuid
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import (
    Section, Category, Topic, Post, Profile, PrivateMessage, PostLike, Notification,
    EmailVerification, DailyTip, QuizQuestion, QuizScore, SuccessStory, FreelanceJob,
    JobProposal, JobReview, Skill, Badge, UserQuizAttempt, JobPayment, Donation,
    SiteSettings, BlogCategory, BlogPost, DonationTier
)
from .forms import RegisterForm, NewTopicForm, PostForm, JobPostForm, ProposalForm
from .email_utils import send_topic_reply_notification, send_private_message_notification
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import (
    SectionSerializer, TopicSerializer, PostSerializer, FreelanceJobSerializer,
    JobReviewSerializer, DailyTipSerializer, QuizQuestionSerializer, QuizScoreSerializer, SuccessStorySerializer
)
from functools import wraps


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
    }
    return render(request, 'forum/home.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    """Next.js Frontend için Anasayfa API Endpoint'i"""

    # 1. İstatistikler
    stats = {
        'total_topics': Topic.objects.count(),
        'total_posts': Post.objects.count(),
        'total_users': User.objects.count(),
        'completed_jobs': FreelanceJob.objects.filter(status='completed').count()
    }

    # 2. Bölümler ve Kategoriler
    sections = Section.objects.all().order_by('order')
    sections_data = SectionSerializer(sections, many=True).data

    # 3. Popüler Konular
    popular_topics = Topic.objects.select_related('starter', 'category').annotate(
        replies_count=Count('posts')
    ).order_by('-views')[:5]
    popular_topics_data = TopicSerializer(popular_topics, many=True).data

    # 4. Son Aktiviteler (Sadece Postlar - Basitleştirilmiş)
    recent_posts = Post.objects.select_related('created_by', 'topic').order_by('-created_at')[:10]
    recent_activities_data = PostSerializer(recent_posts, many=True).data

    # 5. Günün İpucu
    daily_tip = DailyTip.get_today_tip()
    daily_tip_data = DailyTipSerializer(daily_tip).data if daily_tip else None

    # 6. Quiz Liderlik
    quiz_leaderboard = QuizScore.objects.select_related('user', 'user__profile').order_by('-correct_answers')[:5]
    quiz_leaderboard_data = QuizScoreSerializer(quiz_leaderboard, many=True).data

    # 7. Freelance İlanlar
    recent_jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category').order_by('-created_at')[:5]
    recent_jobs_data = FreelanceJobSerializer(recent_jobs, many=True).data

    featured_jobs = FreelanceJob.objects.filter(status='open', is_featured=True).select_related('owner', 'category').order_by('-created_at')[:4]
    featured_jobs_data = FreelanceJobSerializer(featured_jobs, many=True).data

    # 8. Başarı Hikayesi
    featured_story = SuccessStory.objects.filter(is_featured=True).first()
    if not featured_story:
        featured_story = SuccessStory.objects.order_by('?').first()
    featured_story_data = SuccessStorySerializer(featured_story).data if featured_story else None

    # 9. Sosyal Kanıt (Reviews)
    recent_reviews = JobReview.objects.filter(is_approved=True).select_related('reviewer', 'reviewed_user', 'job').order_by('-created_at')[:5]
    recent_reviews_data = JobReviewSerializer(recent_reviews, many=True).data

    return Response({
        'stats': stats,
        'sections': sections_data,
        'popular_topics': popular_topics_data,
        'recent_activities': recent_activities_data,
        'daily_tip': daily_tip_data,
        'quiz_leaderboard': quiz_leaderboard_data,
        'recent_jobs': recent_jobs_data,
        'featured_jobs': featured_jobs_data,
        'featured_story': featured_story_data,
        'recent_reviews': recent_reviews_data
    })

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
        message = f"Sayın {expert.username},

'{job.title}' ilanı için verdiğiniz teklif yöneticiler tarafından silinmiştir.

Sebep: {reason}

Lütfen topluluk kurallarına dikkat ediniz."
        
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
        message = f"Sayın {expert.username},

'{job.title}' ilanı için verdiğiniz teklif yöneticiler tarafından reddedilmiştir.

Sebep: {reason}"
        
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
    # Pinned konular en üstte, sonra tarihe göre sırala
    topics = category.topics.prefetch_related('tags').annotate(replies_count=Count('posts')).order_by('-is_pinned', '-created_at')
    return render(request, 'forum/category_topics.html', {'category': category, 'topics': topics})

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
                f"Merhaba {user.username},

"