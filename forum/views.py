from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.db.models import Count, Sum, Q
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import timedelta
from .models import Section, Category, Topic, Post, Profile, PrivateMessage, PostLike, Notification, EmailVerification, DailyTip, QuizQuestion, QuizScore, SuccessStory, FreelanceJob, JobProposal, Skill
from .forms import RegisterForm, NewTopicForm, PostForm, JobPostForm, ProposalForm
from .email_utils import send_topic_reply_notification, send_private_message_notification

# --- ANA SAYFA ---
def home(request):
    sections = Section.objects.all().order_by('order')

    # Widget verileri
    # İstatistikler
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    total_views = Topic.objects.aggregate(total=Sum('views'))['total'] or 0

    # Son tartışmalar (son 5 aktif konu)
    recent_topics = Topic.objects.select_related('starter', 'category').annotate(
        replies_count=Count('posts')
    ).order_by('-created_at')[:5]

    # Popüler konular (en çok görüntülenen 5 konu)
    popular_topics = Topic.objects.select_related('starter', 'category').annotate(
        replies_count=Count('posts')
    ).order_by('-views')[:5]

    # Son aktiviteler (son 10 post)
    recent_activities = Post.objects.select_related('created_by', 'topic').order_by('-created_at')[:10]

    # Günün İpucu
    daily_tip = DailyTip.get_today_tip()

    # Quiz Sorusu
    quiz_question = QuizQuestion.get_random_question()

    # Haftanın Başarı Hikayesi
    featured_story = SuccessStory.objects.filter(is_featured=True).first()
    if not featured_story:
        featured_story = SuccessStory.objects.order_by('?').first()

    # Freelance Market - Son İlanlar
    recent_jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category').order_by('-created_at')[:5]

    context = {
        'sections': sections,
        # İstatistikler
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
        'total_views': total_views,
        # Widgetlar
        'recent_topics': recent_topics,
        'popular_topics': popular_topics,
        'recent_activities': recent_activities,
        'daily_tip': daily_tip,
        'quiz_question': quiz_question,
        'featured_story': featured_story,
        'recent_jobs': recent_jobs,
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

def success_stories(request):
    stories = SuccessStory.objects.all().order_by('-is_featured', '-created_at')
    form = None

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SuccessStoryForm(request.POST)
            if form.is_valid():
                story = form.save(commit=False)
                story.user = request.user
                # Text alanlarını listeye çevir
                story.achievements = [line.strip() for line in form.cleaned_data['achievements_text'].split('\n') if line.strip()]
                story.resources = [line.strip() for line in form.cleaned_data['resources_text'].split('\n') if line.strip()]
                story.save()
                messages.success(request, 'Harika! Başarı hikayeniz paylaşıldı.')
                return redirect('success_stories')
        else:
            form = SuccessStoryForm()

    return render(request, 'forum/success_stories.html', {'stories': stories, 'form': form})

# --- FREELANCE MARKET ---
def job_list(request):
    sort = request.GET.get('sort', 'newest')
    jobs = FreelanceJob.objects.filter(status='open').select_related('owner', 'category')

    if sort == 'views':
        jobs = jobs.order_by('-views', '-created_at')
    elif sort == 'proposals':
        jobs = jobs.annotate(proposal_count_annotated=Count('proposals')).order_by('-proposal_count_annotated', '-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    return render(request, 'forum/market/job_list.html', {'jobs': jobs, 'current_sort': sort})

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.save()
            messages.success(request, 'İş ilanı başarıyla oluşturuldu.')
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
def job_detail(request, pk):
    job = get_object_or_404(FreelanceJob, pk=pk)
    
    # Görüntülenme sayısını artır
    job.views += 1
    job.save()

    user_proposal = None
    proposal_form = None
    
    # Teklif verme yetkisi kontrolü
    is_expert = JobProposal.can_propose(request.user)
    
    if request.user == job.owner:
        # İlan sahibi ise teklifleri görsün
        proposals = job.proposals.select_related('expert', 'expert__profile').all()
    else:
        proposals = None
        # Kullanıcı daha önce teklif vermiş mi?
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

    return render(request, 'forum/market/job_detail.html', {
        'job': job,
        'proposals': proposals,
        'user_proposal': user_proposal,
        'proposal_form': proposal_form,
        'is_liked': is_liked,
        'is_saved': is_saved,
        'is_expert': is_expert,
        'similar_jobs': similar_jobs
    })

@login_required
def my_jobs(request):
    # Kullanıcının açtığı ilanlar
    posted_jobs = FreelanceJob.objects.filter(owner=request.user).order_by('-created_at')
    # Kullanıcının verdiği teklifler
    my_proposals = JobProposal.objects.filter(expert=request.user).select_related('job').order_by('-created_at')
    # Kullanıcının kaydettiği ilanlar
    saved_jobs = request.user.saved_jobs.all().order_by('-created_at')
    
    return render(request, 'forum/market/my_jobs.html', {
        'posted_jobs': posted_jobs,
        'my_proposals': my_proposals,
        'saved_jobs': saved_jobs
    })

# --- BÖLÜM DETAY ---
def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk)
    categories = section.categories.all()
    return render(request, 'forum/section_detail.html', {'section': section, 'categories': categories})

# --- KATEGORİ VE KONULAR ---
def category_topics(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # Pinned konular en üstte, sonra tarihe göre sırala
    topics = category.topics.annotate(replies_count=Count('posts')).order_by('-is_pinned', '-created_at')
    return render(request, 'forum/category_topics.html', {'category': category, 'topics': topics})

# --- KONU DETAY VE CEVAP YAZMA ---
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
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
def new_topic(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.starter = request.user
            topic.save()
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
        profile.linkedin = request.POST.get('linkedin', '')
        profile.twitter = request.POST.get('twitter', '')
        profile.github = request.POST.get('github', '')
        profile.orcid = request.POST.get('orcid', '')
        profile.google_scholar = request.POST.get('google_scholar', '')

        # Dosyalar
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        if 'cover_image' in request.FILES:
            profile.cover_image = request.FILES['cover_image']
        
        # Ayarlar
        profile.email_on_reply = request.POST.get('email_on_reply') == 'on'
        profile.email_on_private_message = request.POST.get('email_on_private_message') == 'on'
        profile.is_public = request.POST.get('is_public') == 'on'
        profile.show_email = request.POST.get('show_email') == 'on'

        # Yetenekler (Skills)
        selected_skills = request.POST.getlist('skills')
        profile.skills.set(selected_skills)

        profile.save()
        
        messages.success(request, "Profiliniz başarıyla güncellendi.")
        return redirect('profile_edit')
    
    return render(request, 'forum/profile_edit.html', {'user': user, 'profile': profile, 'all_skills': all_skills})

# --- GELEN KUTUSU ---
@login_required
def inbox(request):
    received_messages = PrivateMessage.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'forum/inbox.html', {'received_messages': received_messages})

# --- ÖZEL MESAJ GÖNDER ---
@login_required
def send_message(request, username):
    receiver = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            PrivateMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message_content
            )
            
            # ✅ EMAIL BİLDİRİMİ GÖNDER
            send_private_message_notification(request.user, receiver, message_content)
            
            messages.success(request, f"{receiver.username} kullanıcısına mesajınız gönderildi!")
            return redirect('profile_detail', username=username)
    
    return render(request, 'forum/send_message.html', {'receiver': receiver})

# --- PROFİL DETAY ---
def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    posted_jobs = FreelanceJob.objects.filter(owner=profile_user).order_by('-created_at')
    return render(request, 'forum/profile_detail.html', {'profile_user': profile_user, 'posted_jobs': posted_jobs})

# --- DİĞER ---
def about(request):
    return render(request, 'forum/about.html')

def contact(request):
    return render(request, 'forum/contact.html')

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


# --- AI ASISTAN ---
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


# --- ADMİN DASHBOARD ---
@staff_member_required
def admin_dashboard(request):
    """Admin için istatistik paneli"""
    from django.db.models.functions import TruncDate, TruncMonth
    from collections import OrderedDict

    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    # === GENEL İSTATİSTİKLER ===
    total_users = User.objects.count()
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_views = Topic.objects.aggregate(total=Sum('views'))['total'] or 0

    # Bugünkü istatistikler
    today_users = User.objects.filter(date_joined__date=today).count()
    today_topics = Topic.objects.filter(created_at__date=today).count()
    today_posts = Post.objects.filter(created_at__date=today).count()

    # Son 7 gün
    week_users = User.objects.filter(date_joined__date__gte=last_7_days).count()
    week_topics = Topic.objects.filter(created_at__date__gte=last_7_days).count()
    week_posts = Post.objects.filter(created_at__date__gte=last_7_days).count()

    # === KULLANICI ANALİZİ ===
    # Doğrulanmış/Doğrulanmamış kullanıcılar
    verified_users = Profile.objects.filter(email_verified=True).count()
    unverified_users = Profile.objects.filter(email_verified=False).count()

    # Hesap türlerine göre dağılım
    account_types = Profile.objects.values('account_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Rütbelere göre dağılım
    rank_distribution = Profile.objects.values('rank').annotate(
        count=Count('id')
    ).order_by('-count')

    # === SON 7 GÜNLÜK TREND (Grafik için) ===
    # Kullanıcı kayıtları
    user_trend = []
    topic_trend = []
    post_trend = []
    labels = []

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        labels.append(date.strftime('%d %b'))
        user_trend.append(User.objects.filter(date_joined__date=date).count())
        topic_trend.append(Topic.objects.filter(created_at__date=date).count())
        post_trend.append(Post.objects.filter(created_at__date=date).count())

    # === KATEGORİ ANALİZİ ===
    category_stats = Category.objects.annotate(
        topic_count=Count('topics'),
        post_count=Count('topics__posts')
    ).order_by('-topic_count')[:10]

    # === EN AKTİF KULLANICILAR (Son 30 gün) ===
    active_users = User.objects.annotate(
        recent_posts=Count('posts', filter=Q(posts__created_at__date__gte=last_30_days)),
        recent_topics=Count('topics', filter=Q(topics__created_at__date__gte=last_30_days))
    ).filter(
        Q(recent_posts__gt=0) | Q(recent_topics__gt=0)
    ).order_by('-recent_posts')[:10]

    # === POPÜLER KONULAR (Son 7 gün) ===
    popular_topics = Topic.objects.filter(
        created_at__date__gte=last_7_days
    ).annotate(
        reply_count=Count('posts')
    ).order_by('-views', '-reply_count')[:10]

    # === SON AKTİVİTELER ===
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_topics_list = Topic.objects.select_related('starter', 'category').order_by('-created_at')[:5]
    recent_posts = Post.objects.select_related('created_by', 'topic').order_by('-created_at')[:10]

    # === AI KULLANIM İSTATİSTİKLERİ ===
    from django.core.cache import cache
    # Bugün AI kullanan kullanıcı sayısını tahmin et
    ai_usage_today = 0  # Cache'den detaylı bilgi almak için ek kod gerekir

    context = {
        # Genel İstatistikler
        'total_users': total_users,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_views': total_views,

        # Bugün
        'today_users': today_users,
        'today_topics': today_topics,
        'today_posts': today_posts,

        # Bu hafta
        'week_users': week_users,
        'week_topics': week_topics,
        'week_posts': week_posts,

        # Kullanıcı analizi
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'account_types': account_types,
        'rank_distribution': rank_distribution,

        # Grafikler için
        'chart_labels': labels,
        'user_trend': user_trend,
        'topic_trend': topic_trend,
        'post_trend': post_trend,

        # Kategori analizi
        'category_stats': category_stats,

        # En aktif kullanıcılar
        'active_users': active_users,

        # Popüler konular
        'popular_topics': popular_topics,

        # Son aktiviteler
        'recent_users': recent_users,
        'recent_topics_list': recent_topics_list,
        'recent_posts': recent_posts,
    }

    return render(request, 'forum/admin_dashboard.html', context)
