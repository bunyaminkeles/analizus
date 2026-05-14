import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone


def get_dashboard_context():
    """Admin dashboard istatistiklerini döndürür."""
    from forum.models import (
        Topic, Post, Category, Profile, SuccessStory,
        JobReview, ContactMessage, Donation, FreelanceJob, JobProposal,
    )

    today = timezone.now().date()
    last_7_days  = today - timedelta(days=7)
    last_14_days = today - timedelta(days=14)
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)

    # === GENEL İSTATİSTİKLER ===
    total_users  = User.objects.count()
    total_topics = Topic.objects.count()
    total_posts  = Post.objects.count()
    total_views  = Topic.objects.aggregate(total=Sum('views'))['total'] or 0

    # Bu hafta
    week_users  = User.objects.filter(date_joined__date__gte=last_7_days).count()
    week_topics = Topic.objects.filter(created_at__date__gte=last_7_days).count()
    week_posts  = Post.objects.filter(created_at__date__gte=last_7_days).count()

    # Geçen hafta (delta için)
    prev_week_users  = User.objects.filter(date_joined__date__gte=last_14_days, date_joined__date__lt=last_7_days).count()
    prev_week_topics = Topic.objects.filter(created_at__date__gte=last_14_days, created_at__date__lt=last_7_days).count()
    prev_week_posts  = Post.objects.filter(created_at__date__gte=last_14_days, created_at__date__lt=last_7_days).count()

    def delta_pct(current, previous):
        if previous == 0:
            return None
        return round((current - previous) / previous * 100, 1)

    delta_users  = delta_pct(week_users, prev_week_users)
    delta_topics = delta_pct(week_topics, prev_week_topics)
    delta_posts  = delta_pct(week_posts, prev_week_posts)

    # === HİZMET PAZARI ===
    open_jobs         = FreelanceJob.objects.filter(status='open').count()
    pending_proposals = JobProposal.objects.filter(status='pending').count()
    in_progress_jobs  = FreelanceJob.objects.filter(status='in_progress').count()
    month_completed   = FreelanceJob.objects.filter(status='completed', updated_at__date__gte=last_30_days).count()
    total_completed   = FreelanceJob.objects.filter(status='completed').count()

    # === GELİR ÖZETİ ===
    month_donation_sum = Donation.objects.filter(
        status='approved', created_at__date__gte=last_30_days
    ).aggregate(s=Sum('amount'))['s'] or 0

    total_donation_sum = Donation.objects.filter(
        status='approved'
    ).aggregate(s=Sum('amount'))['s'] or 0

    # Analiz servisleri geliri
    try:
        from tezanaliz.models import TezAnaliz
        month_tezanaliz_count = TezAnaliz.objects.filter(
            status='completed', created_at__date__gte=last_30_days
        ).count()
        total_tezanaliz_count = TezAnaliz.objects.filter(status='completed').count()
    except Exception:
        month_tezanaliz_count = total_tezanaliz_count = 0

    try:
        from bibliometrics.models import BibliometricJob
        month_biblio_count = BibliometricJob.objects.filter(
            status='completed', job_type='full', created_at__date__gte=last_30_days
        ).count()
        total_biblio_count = BibliometricJob.objects.filter(status='completed', job_type='full').count()
    except Exception:
        month_biblio_count = total_biblio_count = 0

    # === DAU / MAU ===
    dau = User.objects.filter(last_login__date=today).count()
    mau = User.objects.filter(last_login__date__gte=last_30_days).count()

    # === İSTATİSTİK ARAÇLARI ===
    try:
        from istatistik.models import IstatistikJob
        istatistik_month = IstatistikJob.objects.filter(
            status='completed', created_at__date__gte=last_30_days
        ).count()
        istatistik_total = IstatistikJob.objects.filter(status='completed').count()
        cronbach_month  = IstatistikJob.objects.filter(tool='cronbach',  status='completed', created_at__date__gte=last_30_days).count()
        normallik_month = IstatistikJob.objects.filter(tool='normallik', status='completed', created_at__date__gte=last_30_days).count()
        betimsel_month  = IstatistikJob.objects.filter(tool='betimsel',  status='completed', created_at__date__gte=last_30_days).count()
        cronbach_total  = IstatistikJob.objects.filter(tool='cronbach',  status='completed').count()
        normallik_total = IstatistikJob.objects.filter(tool='normallik', status='completed').count()
        betimsel_total  = IstatistikJob.objects.filter(tool='betimsel',  status='completed').count()
    except Exception:
        istatistik_month = istatistik_total = 0
        cronbach_month = normallik_month = betimsel_month = 0
        cronbach_total = normallik_total = betimsel_total = 0

    # === SERVİS İSTATİSTİKLERİ ===
    try:
        from openalex.models import AlexSearchJob
        openalex_month = AlexSearchJob.objects.filter(created_at__date__gte=last_30_days).count()
        openalex_total = AlexSearchJob.objects.count()
    except Exception:
        openalex_month = openalex_total = 0

    try:
        from yoktez.models import YokTezSearchJob
        yoktez_month = YokTezSearchJob.objects.filter(created_at__date__gte=last_30_days).count()
        yoktez_total = YokTezSearchJob.objects.count()
    except Exception:
        yoktez_month = yoktez_total = 0

    try:
        from bibliometrics.models import BibliometricJob
        biblio_month = BibliometricJob.objects.filter(created_at__date__gte=last_30_days).count()
        biblio_total = BibliometricJob.objects.count()
    except Exception:
        biblio_month = biblio_total = 0

    try:
        from oaipmh.models import OAISearchJob
        oaipmh_month = OAISearchJob.objects.filter(created_at__date__gte=last_30_days).count()
        oaipmh_total = OAISearchJob.objects.count()
    except Exception:
        oaipmh_month = oaipmh_total = 0

    # === KULLANICI ANALİZİ ===
    verified_users   = Profile.objects.filter(email_verified=True).count()
    unverified_users = Profile.objects.filter(email_verified=False).count()

    # E-posta doğrulama detayları
    from forum.models import EmailVerification
    email_verify_rate = round(verified_users / max(1, total_users) * 100, 1)

    # Son 7 günde kayıt olup henüz doğrulamayan kullanıcılar
    unverified_recent = User.objects.filter(
        date_joined__date__gte=last_7_days,
        profile__email_verified=False
    ).select_related('profile').order_by('-date_joined')[:15]

    # 7 günden eski ama hâlâ doğrulanmamış (takılı kalan)
    unverified_old_count = User.objects.filter(
        date_joined__date__lt=last_7_days,
        profile__email_verified=False
    ).count()

    # Bugün doğrulama yapanlar
    verified_today = Profile.objects.filter(
        email_verified=True,
        user__date_joined__date=today
    ).count()

    rank_distribution = Profile.objects.values('rank').annotate(
        count=Count('id')
    ).order_by('-count')

    # === GRAFİK VERİSİ ===
    from django.db.models.functions import TruncDate, TruncWeek

    # 7 günlük (günlük)
    def build_daily_trend(days):
        start = today - timedelta(days=days - 1)
        u = {r['day']: r['cnt'] for r in
             User.objects.filter(date_joined__date__gte=start)
             .annotate(day=TruncDate('date_joined')).values('day').annotate(cnt=Count('id'))}
        t = {r['day']: r['cnt'] for r in
             Topic.objects.filter(created_at__date__gte=start)
             .annotate(day=TruncDate('created_at')).values('day').annotate(cnt=Count('id'))}
        p = {r['day']: r['cnt'] for r in
             Post.objects.filter(created_at__date__gte=start)
             .annotate(day=TruncDate('created_at')).values('day').annotate(cnt=Count('id'))}
        labels, ud, td, pd = [], [], [], []
        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime('%d %b'))
            ud.append(u.get(d, 0))
            td.append(t.get(d, 0))
            pd.append(p.get(d, 0))
        return labels, ud, td, pd

    # 90 günlük (haftalık)
    def build_weekly_trend(weeks):
        start = today - timedelta(weeks=weeks)
        u = {r['wk']: r['cnt'] for r in
             User.objects.filter(date_joined__date__gte=start)
             .annotate(wk=TruncWeek('date_joined')).values('wk').annotate(cnt=Count('id'))}
        t = {r['wk']: r['cnt'] for r in
             Topic.objects.filter(created_at__date__gte=start)
             .annotate(wk=TruncWeek('created_at')).values('wk').annotate(cnt=Count('id'))}
        p = {r['wk']: r['cnt'] for r in
             Post.objects.filter(created_at__date__gte=start)
             .annotate(wk=TruncWeek('created_at')).values('wk').annotate(cnt=Count('id'))}
        labels, ud, td, pd = [], [], [], []
        from datetime import date as date_cls
        for i in range(weeks - 1, -1, -1):
            wk_date = today - timedelta(weeks=i)
            # haftanın başına hizala (pazartesi)
            wk_start = wk_date - timedelta(days=wk_date.weekday())
            # TruncWeek returns datetime, convert to date for lookup
            wk_dt = timezone.make_aware(
                timezone.datetime(wk_start.year, wk_start.month, wk_start.day)
            )
            labels.append(wk_start.strftime('%d %b'))
            ud.append(u.get(wk_dt, 0))
            td.append(t.get(wk_dt, 0))
            pd.append(p.get(wk_dt, 0))
        return labels, ud, td, pd

    labels7,  u7,  t7,  p7  = build_daily_trend(7)
    labels30, u30, t30, p30 = build_daily_trend(30)
    labels90, u90, t90, p90 = build_weekly_trend(13)  # 13 hafta ≈ 90 gün

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

    pending_stories  = SuccessStory.objects.filter(approval_status='pending').select_related('user')
    pending_reviews  = JobReview.objects.filter(is_approved=False).select_related('reviewer', 'reviewed_user', 'job')
    unread_contacts  = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:20]
    pending_donations = Donation.objects.filter(status='pending').select_related('user').order_by('-created_at')

    # === SON KAYITLAR ===
    recent_users = User.objects.order_by('-date_joined')[:12]
    recent_topics_list = Topic.objects.select_related('starter', 'category').order_by('-created_at')[:5]

    # === PLATFORM HEALTH SCORE ===
    user_growth_score    = min(40, int(week_users / max(1, total_users) * 4000))
    content_growth_score = min(40, int((week_topics + week_posts) / max(1, total_topics + total_posts) * 4000))
    pending_total        = (pending_stories.count() + pending_reviews.count() +
                            unread_contacts.count() + pending_donations.count())
    queue_health_score   = max(0, 20 - pending_total)
    health_score         = user_growth_score + content_growth_score + queue_health_score

    if health_score >= 70:
        health_label, health_color = 'Mükemmel', '#10b981'
    elif health_score >= 40:
        health_label, health_color = 'İyi', '#38bdf8'
    elif health_score >= 20:
        health_label, health_color = 'Orta', '#f59e0b'
    else:
        health_label, health_color = 'Düşük', '#ef4444'

    return {
        # DAU / MAU
        'dau': dau,
        'mau': mau,
        # İstatistik araçları
        'istatistik_month': istatistik_month,
        'istatistik_total': istatistik_total,
        'cronbach_month': cronbach_month,
        'normallik_month': normallik_month,
        'betimsel_month': betimsel_month,
        'cronbach_total': cronbach_total,
        'normallik_total': normallik_total,
        'betimsel_total': betimsel_total,
        # Genel
        'total_users': total_users,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_views': total_views,
        # Bu hafta
        'week_users': week_users,
        'week_topics': week_topics,
        'week_posts': week_posts,
        # Delta
        'delta_users': delta_users,
        'delta_topics': delta_topics,
        'delta_posts': delta_posts,
        # Hizmet Pazarı
        'open_jobs': open_jobs,
        'pending_proposals': pending_proposals,
        'in_progress_jobs': in_progress_jobs,
        'month_completed': month_completed,
        'total_completed': total_completed,
        # Gelir
        'month_donation_sum': month_donation_sum,
        'total_donation_sum': total_donation_sum,
        'month_tezanaliz_count': month_tezanaliz_count,
        'total_tezanaliz_count': total_tezanaliz_count,
        'month_biblio_count': month_biblio_count,
        'total_biblio_count': total_biblio_count,
        # Servis istatistikleri
        'openalex_month': openalex_month,
        'openalex_total': openalex_total,
        'yoktez_month': yoktez_month,
        'yoktez_total': yoktez_total,
        'biblio_month': biblio_month,
        'biblio_total': biblio_total,
        'oaipmh_month': oaipmh_month,
        'oaipmh_total': oaipmh_total,
        # Grafik verileri
        'chart_labels_json':    json.dumps(labels7),
        'user_trend_json':      json.dumps(u7),
        'topic_trend_json':     json.dumps(t7),
        'post_trend_json':      json.dumps(p7),
        'chart_labels_30_json': json.dumps(labels30),
        'user_trend_30_json':   json.dumps(u30),
        'topic_trend_30_json':  json.dumps(t30),
        'post_trend_30_json':   json.dumps(p30),
        'chart_labels_90_json': json.dumps(labels90),
        'user_trend_90_json':   json.dumps(u90),
        'topic_trend_90_json':  json.dumps(t90),
        'post_trend_90_json':   json.dumps(p90),
        # Kullanıcı analizi
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'email_verify_rate': email_verify_rate,
        'unverified_recent': unverified_recent,
        'unverified_old_count': unverified_old_count,
        'verified_today': verified_today,
        'rank_distribution': rank_distribution,
        'category_stats': category_stats,
        'active_users': active_users,
        # Onay merkezi
        'pending_linkedin_verifications': pending_linkedin_verifications,
        'pending_stories': pending_stories,
        'pending_reviews': pending_reviews,
        'unread_contacts': unread_contacts,
        'pending_donations': pending_donations,
        # Son aktiviteler
        'recent_users': recent_users,
        'recent_topics_list': recent_topics_list,
        # Platform Health
        'health_score': health_score,
        'health_label': health_label,
        'health_color': health_color,
    }
