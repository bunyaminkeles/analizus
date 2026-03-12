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
