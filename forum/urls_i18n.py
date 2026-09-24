"""Çok dilli (tr/en/de) URL'ler — analizdestek/urls.py'de i18n_patterns() ile sarılır.

Bu path'ler forum/urls.py'den taşındı çünkü forum/urls.py'nin geri kalanı
(forum, blog, DM, cron endpoint'leri vb.) kapsam dışı — bkz.
tasks/todo.md "Çok Dilli Yayın (EN/DE)" bölümü. Market yalnızca arayüz
düzeyinde dahil (23 Eylül 2026): ilan içerikleri ve TL fiyatlar çevrilmez.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    # Kayıt sonrası akış (forum/urls.py'den taşındı, 24 Eylül 2026)
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('onboarding/', views.onboarding, name='onboarding'),
    # AI Asistan tam sayfa (forum/urls.py'den taşındı, 24 Eylül 2026)
    path('ai-asistan/', views.ai_assistant, name='ai_assistant'),
    # Gizlilik / KVKK + GDPR (forum/urls.py'den taşındı, 24 Eylül 2026)
    path('gizlilik-politikasi/', views.gizlilik_politikasi, name='gizlilik_politikasi'),
    path('proje-talebi/', views.proje_talebi, name='proje_talebi'),
    path('ai-cozumler/', views.ai_cozumler, name='ai_cozumler'),
    path('egitim/', views.egitim, name='egitim'),
    path('egitim-talebi/', views.egitim_talebi, name='egitim_talebi'),
    path('egitim/<slug:slug>/', views.egitim_detay, name='egitim_detay'),

    # Freelance Market (yalnızca arayüz çevirisi)
    path('market/', views.job_list, name='job_list'),
    path('market/new/', views.post_job, name='post_job'),
    path('market/job/<int:pk>/', views.job_detail, name='job_detail'),
    path('market/job/<int:pk>/close/', views.close_job, name='close_job'),
    path('market/job/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('market/job/<int:pk>/accept/<int:proposal_id>/', views.accept_proposal, name='accept_proposal'),
    path('market/job/<int:job_pk>/proposal/<int:proposal_id>/manage/', views.admin_manage_proposal, name='admin_manage_proposal'),
    path('market/job/<int:pk>/review/', views.add_job_review, name='add_job_review'),
    path('market/job/<int:pk>/like/', views.toggle_job_like, name='toggle_job_like'),
    path('market/job/<int:pk>/bookmark/', views.toggle_job_bookmark, name='toggle_job_bookmark'),
    path('market/my-jobs/', views.my_jobs, name='my_jobs'),
    path('market/job/<int:pk>/promote/', views.promote_job, name='promote_job'),
    path('market/job/<int:pk>/payment-transferred/', views.mark_payment_transferred, name='mark_payment_transferred'),

    # Kurumsal sayfalar (24 Eylül 2026)
    path('hakkimizda/', views.about, name='about'),
    path('iletisim/', views.contact, name='contact'),
    path('hangi-test/', views.hangi_test, name='hangi_test'),
]
