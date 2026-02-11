import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone


def get_dashboard_context():
    """Admin dashboard istatistiklerini döndürür."""
    from forum.models import (
        Topic, Post, Category, Profile, SuccessStory,
        JobReview, ContactMessage, Donation,
    )

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
    verified_users = Profile.objects.filter(email_verified=True).count()
    unverified_users = Profile.objects.filter(email_verified=False).count()

    account_types = Profile.objects.values('account_type').annotate(
        count=Count('id')
    ).order_by('-count')

    rank_distribution = Profile.objects.values('rank').annotate(
        count=Count('id')
    ).order_by('-count')

    # === SON 7 GÜNLÜK TREND (Grafik için) ===
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

    # === ONAY BEKLEYENLER ===
    pending_linkedin_verifications = Profile.objects.filter(
        linkedin__isnull=False,
        linkedin_verified=False
    ).exclude(linkedin='').select_related('user')

    pending_stories = SuccessStory.objects.filter(approval_status='pending').select_related('user')
    pending_reviews = JobReview.objects.filter(is_approved=False).select_related('reviewer', 'reviewed_user', 'job')
    unread_contacts = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:20]
    pending_donations = Donation.objects.filter(status='pending').select_related('user').order_by('-created_at')

    # === SON AKTİVİTELER ===
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_topics_list = Topic.objects.select_related('starter', 'category').order_by('-created_at')[:5]

    return {
        'total_users': total_users,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_views': total_views,
        'today_users': today_users,
        'today_topics': today_topics,
        'today_posts': today_posts,
        'week_users': week_users,
        'week_topics': week_topics,
        'week_posts': week_posts,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'account_types': account_types,
        'rank_distribution': rank_distribution,
        'chart_labels_json': json.dumps(labels),
        'user_trend_json': json.dumps(user_trend),
        'topic_trend_json': json.dumps(topic_trend),
        'post_trend_json': json.dumps(post_trend),
        'category_stats': category_stats,
        'active_users': active_users,
        'pending_linkedin_verifications': pending_linkedin_verifications,
        'pending_stories': pending_stories,
        'pending_reviews': pending_reviews,
        'unread_contacts': unread_contacts,
        'pending_donations': pending_donations,
        'recent_users': recent_users,
        'recent_topics_list': recent_topics_list,
    }
