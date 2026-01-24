from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from forum.sitemaps import StaticViewSitemap, TopicSitemap, CategorySitemap, JobSitemap

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
    
    # 2. Özel Giriş/Çıkış Sayfaları (Senin belirlediğin şablonlar ile)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # Logout için şablon şart değil, redirect yeterli

    # 3. Forum Uygulaması (En sona koymak çakışmaları önler)
    path('', include('forum.urls')),
    path('i18n/', include('django.conf.urls.i18n')), # DİL MOTORU BURADA

    # 4. SEO - Sitemap & Robots
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]