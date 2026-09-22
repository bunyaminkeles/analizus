"""Çok dilli (tr/en/de) URL'ler — analizdestek/urls.py'de i18n_patterns() ile sarılır.

Bu path'ler forum/urls.py'den taşındı çünkü forum/urls.py'nin geri kalanı
(forum, market, blog, DM, cron endpoint'leri vb.) kapsam dışı — bkz.
tasks/todo.md "Çok Dilli Yayın (EN/DE)" bölümü.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('proje-talebi/', views.proje_talebi, name='proje_talebi'),
    path('ai-cozumler/', views.ai_cozumler, name='ai_cozumler'),
    path('egitim/', views.egitim, name='egitim'),
    path('egitim-talebi/', views.egitim_talebi, name='egitim_talebi'),
    path('egitim/<slug:slug>/', views.egitim_detay, name='egitim_detay'),
]
