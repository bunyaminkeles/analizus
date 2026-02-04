from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from forum.sitemaps import StaticViewSitemap, TopicSitemap, CategorySitemap, JobSitemap
from forum.views import custom_login

sitemaps = {
    'static': StaticViewSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
    'jobs': JobSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Kimlik Doğrulama Yolları
    # Django'nun dahili giriş/çıkış sistemini aktif eder
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. Özel Giriş/Çıkış Sayfaları (Rate limited)
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. Forum Uygulaması (En sona koymak çakışmaları önler)
    path('', include('forum.urls')),
    path('i18n/', include('django.conf.urls.i18n')), # DİL MOTORU BURADA

    # 4. SEO - Sitemap & Robots
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Lokal geliştirmede media dosyalarını servis et
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)