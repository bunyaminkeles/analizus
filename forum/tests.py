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
def test_expert_showcase_includes_expert_with_zero_completed_jobs(client, user):
    """0 tamamlanan projesi olan uzman da Uzmanlarla Tanış vitrininde görünür —
    vitrin artık tamamlanan proje sayısına göre filtrelenmiyor/sıralanmıyor,
    yalnızca reputation (akademik puan) sıralaması kullanılıyor."""
    from forum.models import Profile
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.rank = 'expert'
    profile.is_public = True
    profile.save()

    _prime_home_caches()
    response = client.get('/')
    assert user.username in response.content.decode()


@pytest.mark.django_db
def test_expert_card_shows_profile_title(client, user):
    """Profildeki Ünvan alanı (Profile.title) uzman kartında isim altında görünür."""
    from forum.models import Profile
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.rank = 'expert'
    profile.is_public = True
    profile.title = 'Veri Analisti'
    profile.save()

    _prime_home_caches()
    response = client.get('/')
    assert 'Veri Analisti' in response.content.decode()


@pytest.mark.django_db
def test_expert_card_never_shows_completed_jobs_text(client, user):
    """Uzmanın tamamlanmış işi olsa bile 'tamamlanan proje' metni artık hiç
    render edilmiyor — kart yalnızca uzmanlık alanlarını (skills) ve puanı gösterir."""
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
    assert 'tamamlanan proje' not in response.content.decode()


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


# ─── Madde 10: Son Süpürme Kapanışı ───────────────────────────────────────────

# Madde 1: proje_talebi ön-seçim (source/type → analysis_type <select> "selected")

@pytest.mark.django_db
def test_proje_talebi_preselects_verification(client):
    response = client.get('/proje-talebi/?source=verification&type=verification')
    content = response.content.decode()
    assert '<option value="verification" selected>' in content


@pytest.mark.django_db
def test_proje_talebi_preselects_agentic(client):
    response = client.get('/proje-talebi/?source=agentic&type=agentic')
    content = response.content.decode()
    assert '<option value="agentic" selected>' in content


@pytest.mark.django_db
def test_proje_talebi_preselects_tableau(client):
    response = client.get('/proje-talebi/?source=tableau')
    content = response.content.decode()
    assert '<option value="visualization" selected>' in content


@pytest.mark.django_db
def test_proje_talebi_preselects_bibliometric(client):
    response = client.get('/proje-talebi/?source=bibliometrics')
    content = response.content.decode()
    assert '<option value="bibliometric" selected>' in content


# Madde 4: forum arama boş-durumu varsayılan görünümde gizli

@pytest.mark.django_db
def test_forum_index_no_results_hidden_by_default(client):
    """Arama yapılmamışken '#noResults' bloğu d-none ile gizli kalmalı."""
    response = client.get('/forum/')
    content = response.content.decode()
    assert 'id="noResults" class="text-center text-white-50 py-5 d-none"' in content


# Madde 6: NoIndexMiddleware — dev'de header var, prod'da yok

@pytest.mark.django_db
def test_noindex_header_present_when_not_production(client, settings):
    settings.IS_PRODUCTION = False
    response = client.get('/')
    assert response.get('X-Robots-Tag') == 'noindex, nofollow'


@pytest.mark.django_db
def test_noindex_header_absent_when_production(client, settings):
    settings.IS_PRODUCTION = True
    response = client.get('/')
    assert response.get('X-Robots-Tag') is None


# Madde 7b: Tableau facade — ilk yüklemede gerçek embed DOM'da değil

@pytest.mark.django_db
def test_tableau_facade_no_live_embed_on_initial_load(client):
    """<tableau-viz> yalnızca <template> içinde saklı, ilk yüklemede canlı DOM'da yok."""
    response = client.get('/tableau-analiz/')
    content = response.content.decode()
    assert '<template data-tableau-embed>' in content
    live_dom = content.split('<template data-tableau-embed>')[0]
    assert '<tableau-viz' not in live_dom


# Madde 9: auth sayfaları 200 (mevcut testlerle örtüşür — bkz. test_register_get_returns_200 /
# test_login_get_returns_200 yukarıda, ayrıca burada yinelenmiyor)


# ─── Odalar Faz 1: Üye Gizliliği ──────────────────────────────────────────────

def _create_test_room(creator, slug):
    from forum.models import StudyRoom
    from django.utils import timezone
    import datetime
    return StudyRoom.objects.create(
        title='Test Odası', slug=slug, description='desc', goal='Test hedefi',
        creator=creator, ends_at=timezone.now() + datetime.timedelta(days=30),
        status='active',
    )


@pytest.mark.django_db
def test_studyroom_detail_hides_member_names_from_guest(client, user):
    """Misafir isteğinde hiçbir üye kullanıcı adı response body'de geçmemeli."""
    from forum.models import StudyRoomMembership
    room = _create_test_room(user, 'test-odasi-guest')
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')

    other_user = User.objects.create_user(username='secretmember', password='testpass123')
    StudyRoomMembership.objects.create(room=room, user=other_user, role='member')

    response = client.get(f'/odalar/{room.slug}/')
    content = response.content.decode()
    assert 'secretmember' not in content
    assert user.username not in content  # kurucu adı da misafire kapalı


@pytest.mark.django_db
def test_studyroom_list_hides_creator_name_from_guest(client, user):
    """Liste kartında kurucu adı misafire görünmemeli (rütbe metnine düşer)."""
    _create_test_room(user, 'test-odasi-list-guest')

    response = client.get('/odalar/')
    content = response.content.decode()
    assert user.username not in content


@pytest.mark.django_db
def test_studyroom_detail_shows_creator_to_logged_in_non_member(client, user):
    """Login olmuş ama üye olmayan kullanıcıya kurucu adı görünür (karar: madde 1)."""
    from forum.models import StudyRoomMembership
    room = _create_test_room(user, 'test-odasi-viewer')
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')

    viewer = User.objects.create_user(username='viewer1', password='testpass123')
    client.force_login(viewer)
    response = client.get(f'/odalar/{room.slug}/')
    content = response.content.decode()
    assert user.username in content


# ─── Odalar Faz 2: Bekleme Listesi ────────────────────────────────────────────

@pytest.mark.django_db
def test_studyroom_waitlist_join_rejected_when_room_not_full(client, user):
    """Oda dolu değilken bekleme listesine katılma isteği reddedilir."""
    from forum.models import StudyRoomMembership
    room = _create_test_room(user, 'test-odasi-bos')
    room.max_members = 5
    room.save(update_fields=['max_members'])
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')

    other = User.objects.create_user(username='bekleyen1', password='testpass123')
    client.force_login(other)
    response = client.post(f'/odalar/{room.slug}/bekle/')
    assert response.status_code == 400


@pytest.mark.django_db
def test_studyroom_waitlist_join_succeeds_when_room_full(client, user):
    """Oda dolduğunda bekleme listesine katılma isteği kabul edilir ve kaydediliyor."""
    from forum.models import StudyRoomMembership, StudyRoomWaitlist
    room = _create_test_room(user, 'test-odasi-dolu')
    room.max_members = 1
    room.save(update_fields=['max_members'])
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')

    other = User.objects.create_user(username='bekleyen2', password='testpass123')
    client.force_login(other)
    response = client.post(f'/odalar/{room.slug}/bekle/')
    assert response.status_code == 200
    assert StudyRoomWaitlist.objects.filter(room=room, user=other).exists()


@pytest.mark.django_db
def test_studyroom_leave_notifies_next_waitlist_entry(client, user):
    """Üye ayrılınca bekleme listesindeki ilk kişiye e-posta bildirimi gider."""
    from forum.models import StudyRoomMembership, StudyRoomWaitlist
    room = _create_test_room(user, 'test-odasi-bildirim')
    room.max_members = 2
    room.save(update_fields=['max_members'])
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')

    leaving = User.objects.create_user(username='ayrilanuye', password='testpass123')
    StudyRoomMembership.objects.create(room=room, user=leaving, role='member')

    waiter = User.objects.create_user(
        username='bekleyen3', password='testpass123', email='bekleyen3@example.com'
    )
    StudyRoomWaitlist.objects.create(room=room, user=waiter)

    client.force_login(leaving)
    response = client.post(f'/odalar/{room.slug}/katil/')
    assert response.status_code == 200

    import time
    time.sleep(0.2)  # async e-posta thread'i tamamlansın
    entry = StudyRoomWaitlist.objects.get(room=room, user=waiter)
    assert entry.notified is True


# ─── Odalar Faz 4: Arşiv ───────────────────────────────────────────────────────

@pytest.mark.django_db
def test_studyroom_archived_post_edit_rejected(client, user):
    """Arşivlenmiş odada mesaj düzenleme API'si 403 döner."""
    from forum.models import StudyRoomMembership, StudyRoomPost
    room = _create_test_room(user, 'test-odasi-arsiv-duzenle')
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')
    post = StudyRoomPost.objects.create(room=room, author=user, message='eski mesaj')
    room.status = 'archived'
    room.save(update_fields=['status'])

    client.force_login(user)
    response = client.post(f'/api/room-post/{post.id}/edit/', {'message': 'yeni mesaj'})
    assert response.status_code == 403
    post.refresh_from_db()
    assert post.message == 'eski mesaj'


@pytest.mark.django_db
def test_studyroom_archived_post_delete_rejected(client, user):
    """Arşivlenmiş odada mesaj silme API'si 403 döner."""
    from forum.models import StudyRoomMembership, StudyRoomPost
    room = _create_test_room(user, 'test-odasi-arsiv-sil')
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')
    post = StudyRoomPost.objects.create(room=room, author=user, message='silinmeyecek')
    room.status = 'archived'
    room.save(update_fields=['status'])

    client.force_login(user)
    response = client.post(f'/api/room-post/{post.id}/delete/')
    assert response.status_code == 403
    assert StudyRoomPost.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test_studyroom_list_archived_strip_hidden_when_empty(client):
    """Hiç arşiv oda yokken 'Tamamlanan Odalar' şeridi hiç render edilmez."""
    response = client.get('/odalar/')
    assert 'Tamamlanan Odalar' not in response.content.decode()


@pytest.mark.django_db
def test_studyroom_list_archived_strip_visible_when_nonempty(client, user):
    """Arşivde oda varsa aktif sekme altında 'Tamamlanan Odalar' şeridi görünür."""
    room = _create_test_room(user, 'test-odasi-arsiv-serit')
    room.status = 'archived'
    room.save(update_fields=['status'])

    response = client.get('/odalar/')
    assert 'Tamamlanan Odalar' in response.content.decode()


# ─── Odalar Faz 6: Kilit Ekranı Teaser ─────────────────────────────────────────

@pytest.mark.django_db
def test_studyroom_lock_screen_hides_activity_metrics_when_zero(client, user):
    """Hiç gönderi yokken misafir kilit ekranında aktivite metrik satırı gizli (sıfır kuralı)."""
    room = _create_test_room(user, 'test-odasi-kilit-sifir')

    response = client.get(f'/odalar/{room.slug}/')
    content = response.content.decode()
    assert 'gönderi' not in content.split('Bu odanın yazışmaları')[1].split('Tartışmalara katılmak')[0]


@pytest.mark.django_db
def test_studyroom_lock_screen_shows_activity_metrics_when_posts_exist(client, user):
    """Gönderi varken misafir kilit ekranında gönderi sayısı görünür, ama mesaj içeriği/yazar sızmaz."""
    from forum.models import StudyRoomMembership, StudyRoomPost
    room = _create_test_room(user, 'test-odasi-kilit-dolu')
    StudyRoomMembership.objects.create(room=room, user=user, role='creator')
    StudyRoomPost.objects.create(room=room, author=user, message='gizli-mesaj-icerigi')

    response = client.get(f'/odalar/{room.slug}/')
    content = response.content.decode()
    assert '1 gönderi' in content
    assert 'gizli-mesaj-icerigi' not in content
