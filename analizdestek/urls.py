from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from forum.sitemaps import StaticViewSitemap, TopicSitemap, CategorySitemap, JobSitemap, BlogPostSitemap, IstatistikSitemap, ToolsSitemap
from forum.views import custom_login

sitemaps = {
    'static': StaticViewSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
    'jobs': JobSitemap,
    'blog': BlogPostSitemap,
    'istatistik': IstatistikSitemap,
    'tools': ToolsSitemap,
}

urlpatterns = [
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
    # Django'nun diğer dahili giriş/çıkış sistemini aktif eder
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. Özel Giriş/Çıkış Sayfaları (Rate limited)
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # TR Dizin Tarama
    path('trdizin/', include('trdizin.urls')),

    # OpenAlex Yayın Tarama
    path('openalex/', include('openalex.urls')),

    # Üniversite Tez Arşivi (OAI-PMH)
    path('oaipmh/', include('oaipmh.urls')),

    # YÖK Tez Arama
    path('yoktez/', include('yoktez.urls')),

    # Bibliometrik Analiz
    path('bibliometrics/', include('bibliometrics.urls')),

    # Tez & Makale Analizi
    path('tezanaliz/', include('tezanaliz.urls', namespace='tezanaliz')),

    # TR Dizin Makale Analizi
    path('makaleanaliz/', include('makaleanaliz.urls', namespace='makaleanaliz')),

    # İstatistik Analiz Araçları
    path('istatistik/', include('istatistik.urls', namespace='istatistik')),

    # Unified Analiz Konsolu (/analiz/ prefix)
    path('analiz/', include('istatistik.urls_analiz')),

    # 4. Forum Uygulaması (En sona koymak çakışmaları önler)
    path('', include('forum.urls')),
    path('i18n/', include('django.conf.urls.i18n')), # DİL MOTORU BURADA

    # 4. SEO - Sitemap & Robots
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('534e22a9f9e4d375119c5bc6d006aad0.txt', lambda r: HttpResponse('534e22a9f9e4d375119c5bc6d006aad0', content_type='text/plain')),
    path('46d2a083d40a42108f68727e20395ab8.txt', lambda r: HttpResponse('46d2a083d40a42108f68727e20395ab8', content_type='text/plain')),
]

# Lokal geliştirmede media dosyalarını servis et
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)