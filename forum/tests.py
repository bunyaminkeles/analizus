"""
Forum app için kritik akış testleri.
Kapsam: cron auth, health check, job status geçişleri, profil güncelleme.
"""
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='staffuser', password='testpass123', is_staff=True)


# ─── Cron Auth ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_cron_health_no_auth(client):
    """Health check endpoint auth gerektirmez."""
    response = client.get('/api/cron/health/')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert 'checks' in data


@pytest.mark.django_db
def test_cron_cleanup_rejects_wrong_secret(client):
    """Yanlış secret ile cron endpoint 403 döner."""
    response = client.get('/api/cron/cleanup-s3/', HTTP_X_CRON_SECRET='wrong-secret')
    assert response.status_code == 403


@pytest.mark.django_db
def test_cron_cleanup_accepts_correct_secret(client, settings):
    """Doğru secret ile cron endpoint erişilebilir."""
    settings.CRON_SECRET_KEY = 'test-secret'
    import os
    os.environ['CRON_SECRET_KEY'] = 'test-secret'
    response = client.get('/api/cron/cleanup-s3/', HTTP_X_CRON_SECRET='test-secret')
    # 200 veya hata mesajı (S3 bağlantısı olmasa bile auth geçmeli)
    assert response.status_code != 403


# ─── Health Check ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_health_check_returns_db_status(client):
    """Health check DB durumunu döndürür."""
    response = client.get('/api/cron/health/')
    data = response.json()
    assert 'db' in data['checks']


@pytest.mark.django_db
def test_health_check_db_ok(client):
    """DB bağlantısı başarılı ise 'ok' döner."""
    response = client.get('/api/cron/health/')
    data = response.json()
    assert data['checks']['db'] == 'ok'


# ─── Profil İstatistik Güncelleme ─────────────────────────────────────────────

@pytest.mark.django_db
def test_update_stats_no_posts(user):
    """Post yokken total_likes_received 0 olmalı."""
    from forum.models import Profile
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.update_stats()
    assert profile.total_likes_received == 0
    assert profile.total_posts == 0
    assert profile.total_topics == 0


@pytest.mark.django_db
def test_update_stats_with_posts(user):
    """Post varken aggregate ile doğru likes sayısı hesaplanır."""
    from forum.models import Profile, Section, Category, Topic, Post
    profile, _ = Profile.objects.get_or_create(user=user)

    section = Section.objects.create(title='Test Bölüm', order=1)
    category = Category.objects.create(title='Test Kat', slug='test-kat', section=section)
    topic = Topic.objects.create(subject='Test Konu', category=category, starter=user)
    Post.objects.create(topic=topic, created_by=user, message='msg1', likes=5)
    Post.objects.create(topic=topic, created_by=user, message='msg2', likes=3)

    profile.update_stats()
    assert profile.total_likes_received == 8
    assert profile.total_posts == 2


# ─── OpenAlex Job Status Geçişleri ───────────────────────────────────────────

@pytest.mark.django_db
def test_alex_job_mark_running(user):
    """Job pending → running geçişi."""
    from openalex.models import AlexSearchJob
    job = AlexSearchJob.objects.create(user=user)
    assert job.status == 'pending'
    job.mark_running()
    assert job.status == 'running'


@pytest.mark.django_db
def test_alex_job_mark_completed(user):
    """Job running → completed geçişi, sonuçlar kaydedilir."""
    from openalex.models import AlexSearchJob
    job = AlexSearchJob.objects.create(user=user, status='running')
    job.mark_completed(
        demo_results=[{'title': 'Test'}],
        all_results=[{'title': 'Test'}],
        total_count=1,
        api_query='title.search:Test',
    )
    job.refresh_from_db()
    assert job.status == 'completed'
    assert job.total_results == 1


@pytest.mark.django_db
def test_alex_job_mark_failed(user):
    """Job failed olarak işaretlenir, hata mesajı kaydedilir."""
    from openalex.models import AlexSearchJob
    job = AlexSearchJob.objects.create(user=user, status='running')
    job.mark_failed('Bağlantı hatası')
    job.refresh_from_db()
    assert job.status == 'failed'
    assert 'Bağlantı hatası' in job.error_message


# ─── YÖK Tez Job Status Geçişleri ────────────────────────────────────────────

@pytest.mark.django_db
def test_yoktez_job_daily_limit_normal_user(user):
    """Normal kullanıcı için günlük limit 1 olmalı."""
    from yoktez.models import YokTezSearchJob
    limit = YokTezSearchJob.get_daily_limit(user)
    assert limit == 1


@pytest.mark.django_db
def test_yoktez_job_daily_limit_staff(staff_user):
    """Staff kullanıcı için günlük limit sınırsız (9999) olmalı."""
    from yoktez.models import YokTezSearchJob
    limit = YokTezSearchJob.get_daily_limit(staff_user)
    assert limit == 9999


# ─── Register View ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_register_get_returns_200(client):
    """Register sayfası GET ile açılır."""
    response = client.get('/register/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_get_returns_200(client):
    """Login sayfası GET ile açılır."""
    response = client.get('/login/')
    assert response.status_code == 200


# ─── Sıfır Kuralı (Zero-State Sigortası) ──────────────────────────────────────
# home_stats / home_experts view cache'i test'ler arası sızmasın diye her testte
# temizlenir; science_news_feed cache'i ise canlı RSS isteği tetiklememek için
# boş liste ile önceden doldurulur (get_science_news kendi ayrı cache key'ini
# kullanır, bkz. forum/news_utils.py).

def _prime_home_caches(stats_override=None):
    from django.core.cache import cache
    cache.delete('home_experts')
    cache.set('science_news_feed', [], 60)
    if stats_override is not None:
        # home_stats DB'den değil enjekte edilen değerden okunur — 0073_seed_initial_users
        # migration'ı testte de 15 kullanıcı seed ettiği için gerçek DB sorgusuyla
        # "hepsi sıfır" senaryosu üretilemez, cache üzerinden zorlanır.
        cache.set('home_stats', stats_override, 300)
    else:
        cache.delete('home_stats')


_ZERO_HOME_STATS = {
    'total_topics': 0, 'total_posts': 0, 'total_users': 0,
    'completed_jobs': 0, 'weekly_new_users': 0, 'open_jobs_count': 0,
    'active_experts_count': 0, 'completed_analyses': 0, 'online_experts': 0,
}


@pytest.mark.django_db
def test_home_stats_band_hidden_when_all_zero(client):
    """Hiç veri yokken istatistik bandı (ax-stats-section) hiç render edilmez."""
    _prime_home_caches(stats_override=_ZERO_HOME_STATS)
    response = client.get('/')
    assert 'ax-stats-section' not in response.content.decode()


@pytest.mark.django_db
def test_home_stats_band_visible_when_nonzero(client, user):
    """En az bir metrik doluyken bant görünür ve o metnik render edilir."""
    from forum.models import Topic, Post, Section, Category
    section = Section.objects.create(title='Test Bölüm', order=1)
    category = Category.objects.create(title='Test Kat', slug='test-kat', section=section)
    Topic.objects.create(subject='Test Konu', category=category, starter=user)

    _prime_home_caches()
    response = client.get('/')
    content = response.content.decode()
    assert 'ax-stats-section' in content
    assert 'Akademik Konu' in content


@pytest.mark.django_db
def test_home_completed_jobs_stat_hidden_when_zero(client, user):
    """Diğer sayaçlar doluyken tamamlanan proje 0'sa yalnızca o kutu gizlenir."""
    from forum.models import Topic, Section, Category
    section = Section.objects.create(title='Test Bölüm', order=1)
    category = Category.objects.create(title='Test Kat', slug='test-kat', section=section)
    Topic.objects.create(subject='Test Konu', category=category, starter=user)

    _prime_home_caches()
    response = client.get('/')
    content = response.content.decode()
    assert 'Aktif Üye' in content
    assert 'Tamamlanan Proje' not in content


@pytest.mark.django_db
def test_home_completed_jobs_stat_visible_when_nonzero(client, user):
    """Tamamlanan iş varsa 'Tamamlanan Proje' kutusu render edilir."""
    from forum.models import FreelanceJob
    FreelanceJob.objects.create(
        owner=user, title='Test İş', description='desc',
        budget_max=1000, status='completed',
    )

    _prime_home_caches()
    response = client.get('/')
    assert 'Tamamlanan Proje' in response.content.decode()


@pytest.mark.django_db
def test_expert_card_hides_completed_jobs_row_when_zero(client, user):
    """Uzman kartında tamamlanan proje 0 ise satır gizlenir, kart kendisi kalır."""
    from forum.models import Profile
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.rank = 'expert'
    profile.is_public = True
    profile.save()

    _prime_home_caches()
    response = client.get('/')
    content = response.content.decode()
    assert user.username in content
    assert 'tamamlanan proje' not in content


@pytest.mark.django_db
def test_expert_card_shows_completed_jobs_row_when_nonzero(client, user):
    """Uzmanın tamamlanmış işi varsa 'X tamamlanan proje' satırı render edilir."""
    from forum.models import Profile, FreelanceJob, JobProposal
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.rank = 'expert'
    profile.is_public = True
    profile.save()

    owner = User.objects.create_user(username='jobowner1', password='testpass123')
    job = FreelanceJob.objects.create(
        owner=owner, title='Test İş', description='desc',
        budget_max=1000, status='completed',
    )
    JobProposal.objects.create(
        job=job, expert=user, price=900, duration='3 gün',
        message='msg', status='accepted',
    )

    _prime_home_caches()
    response = client.get('/')
    assert 'tamamlanan proje' in response.content.decode()


@pytest.mark.django_db
def test_market_stats_strip_hidden_when_all_zero(client):
    """Hiç tamamlanan iş/uzman/son-90-gün verisi yokken istatistik şeridi gizlenir."""
    response = client.get('/market/')
    content = response.content.decode()
    assert 'Tamamlanan İş' not in content
    assert 'Aktif Uzman' not in content
    assert 'Son 90 Günde' not in content


@pytest.mark.django_db
def test_market_stats_strip_visible_when_nonzero(client, user):
    """Tamamlanan iş varsa ilgili kutu (ve yalnızca o kutu grubu) görünür."""
    from forum.models import FreelanceJob
    FreelanceJob.objects.create(
        owner=user, title='Test İş', description='desc',
        budget_max=1000, status='completed',
    )
    response = client.get('/market/')
    assert 'Tamamlanan İş' in response.content.decode()


@pytest.mark.django_db
def test_market_empty_listing_keeps_invite_cta(client):
    """Boş ilan listesi 'davet' metnini korur — sıfır kuralı kapsamı dışında istisna."""
    response = client.get('/market/')
    assert 'Şu anda açık ilan bulunmuyor.' in response.content.decode()
