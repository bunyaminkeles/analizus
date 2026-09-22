from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from forum.sitemaps import StaticViewSitemap, TopicSitemap, CategorySitemap, JobSitemap, BlogPostSitemap, IstatistikSitemap, ToolsSitemap, StudyRoomSitemap, TrainingSitemap
from forum.views import custom_login, tarama_hub

sitemaps = {
    'static': StaticViewSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
    'jobs': JobSitemap,
    'blog': BlogPostSitemap,
    'istatistik': IstatistikSitemap,
    'tools': ToolsSitemap,
    'studyrooms': StudyRoomSitemap,
    'training': TrainingSitemap,
}

# Çok dilli (tr/en/de) kapsam — bkz. tasks/todo.md "Çok Dilli Yayın (EN/DE)".
# prefix_default_language=False: tr (varsayılan) prefix'siz kalır, en/de /en/ /de/ alır.
urlpatterns = i18n_patterns(
    # Ana sayfa, kayıt, proje talebi/danışmanlık/eğitim landing sayfaları
    path('', include('forum.urls_i18n')),

    # Makale Analizi, OpenAlex, Semantic Scholar — uluslararası kaynaklar
    path('makaleanaliz/', include('makaleanaliz.urls', namespace='makaleanaliz')),
    path('openalex/', include('openalex.urls')),
    path('semantic-scholar/', include('semanticscholar.urls')),

    # Unified Analiz Konsolu — 18 istatistik aracının açıklama/giriş sayfaları
    path('analiz/', include('istatistik.urls_analiz')),

    # Özel Giriş/Çıkış Sayfaları (Rate limited). i18n_patterns İÇİNDE olmalı —
    # dışarıda kalırsa (prefix'siz /login/) LocaleMiddleware aktif dili zorla
    # varsayılana (tr) çeker, kullanıcı /en/ veya /de/ sayfasından "Giriş"e
    # tıklayınca dil bağlamı kayboluyordu (22 Eylül 2026, kullanıcı raporu:
    # "dil seçiminden sonra sayfa değiştiğinde otomatik olarak tr'ye geçiliyor").
    # 'login'/'logout' adı django.contrib.auth.urls ile çakışıyordu (reverse()
    # belirsizliği) — bu yüzden aşağıda o include KALDIRILDI, sadece
    # kullanılmayan password_change* elle tanımlandı (bkz. yorum).
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # DİL MOTORU — i18n_patterns İÇİNDE olmalı: set_language view'ı prefix'siz
    # kalırsa (/i18n/setlang/), bu isteğin KENDİSİ prefix'siz olduğu için
    # LocaleMiddleware aktif dili zorla varsayılana (tr) çeker — set_language
    # içindeki translate_url(next, lang) o anda 'tr' aktifken next'i (örn.
    # /en/...) çözmeye çalışır, prefix uyuşmaz, Resolver404, next DEĞİŞMEDEN
    # döner (kullanıcı /en/ veya /de/ sayfasından dil değiştiremez, sessizce
    # aynı sayfada kalır — 22 Eylül 2026, kullanıcı raporu: "de ve tr
    # seçilmiyor, en seçilebiliyor"). i18n_patterns içine alınca istek
    # /en/i18n/setlang/ gibi kendi prefix'ini taşır, aktif dil doğru kalır,
    # translate_url doğru çözer.
    path('i18n/', include('django.conf.urls.i18n')),

    prefix_default_language=False,
)

urlpatterns += [
    path('admin/', admin.site.urls),

    # 1. Kimlik Doğrulama Yolları - Şifre sıfırlama için özel template'ler
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    # django.contrib.auth.urls'ün geri kalanı (yalnızca password_change*,
    # login/logout YUKARIDA i18n_patterns içinde özel view'larla tanımlı —
    # include() kullanılmıyor ki 'login'/'logout' adı çakışmasın). Kod
    # tabanında kullanılmıyor (grep: 0 sonuç) ama Django admin dışı bir
    # yerden çağrılabilir ihtimaline karşı korunuyor.
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # TR Dizin Tarama — kapsam dışı (Türkiye'ye özgü)
    path('trdizin/', include('trdizin.urls')),

    # Üniversite Tez Arşivi (OAI-PMH) — kapsam dışı (17 aktif arşivin hepsi Türk üniversitesi)
    path('oaipmh/', include('oaipmh.urls')),

    # YÖK Tez Arama — kapsam dışı (Türkiye'ye özgü)
    path('yoktez/', include('yoktez.urls')),

    # Bibliometrik Analiz — kapsam dışı
    path('bibliometrics/', include('bibliometrics.urls')),

    # Tez Analizi (YÖK Tez tabanlı) — kapsam dışı
    path('tezanaliz/', include('tezanaliz.urls', namespace='tezanaliz')),

    # YouTube Transcript İndirici — kapsam dışı
    path('transcript/', include('transcript.urls', namespace='transcript')),

    # İstatistik Analiz Araçları — legacy POST/status endpoint'leri (KASITLI dokunulmadı,
    # bkz. analizus.md §26 "istatistik double-duty"; i18n_patterns'e alınmadı)
    path('istatistik/', include('istatistik.urls', namespace='istatistik')),

    # Akademik Tarama Unified Console — kapsam dışı (yoktez/trdizin/oaipmh kartları)
    path('tarama/', tarama_hub, name='tarama_hub'),

    # 4. Forum Uygulaması — geri kalanı (forum, market, blog, DM...) kapsam dışı.
    # En sona koymak çakışmaları önler.
    path('', include('forum.urls')),

    # 4. SEO - Sitemap & Robots
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('534e22a9f9e4d375119c5bc6d006aad0.txt', lambda r: HttpResponse('534e22a9f9e4d375119c5bc6d006aad0', content_type='text/plain')),
    path('46d2a083d40a42108f68727e20395ab8.txt', lambda r: HttpResponse('46d2a083d40a42108f68727e20395ab8', content_type='text/plain')),
]

# Lokal geliştirmede media dosyalarını servis et
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)