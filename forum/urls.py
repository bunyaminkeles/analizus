from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    
    # Profil
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    
    # Mesajlaşma
    path('inbox/', views.inbox, name='inbox'),
    path('send-message/<str:username>/', views.send_message, name='send_message'),  # ✅ YENİ

    # Forum
    path('forum/<slug:slug>/', views.category_topics, name='category_topics'),
    path('forum/<slug:slug>/new/', views.new_topic, name='new_topic'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:pk>/summarize/', views.summarize_topic, name='summarize_topic'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    
    # Bildirim API (AJAX)
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # AI Asistan
    path('ai-asistan/', views.ai_assistant, name='ai_assistant'),
    path('api/ai/suggest/<int:topic_id>/', views.ai_suggest_answer, name='ai_suggest_answer'),

    # E-posta Doğrulama
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Diğer
    path('search/', views.search_result, name='search'),
    path('hakkimizda/', views.about, name='about'),
    path('iletisim/', views.contact, name='contact'),
    
    # Section Detail
    path('section/<int:pk>/', views.section_detail, name='section_detail'),

    # Başarı Hikayeleri
    path('success-stories/', views.success_stories, name='success_stories'),

    # Freelance Market
    path('market/', views.job_list, name='job_list'),
    path('market/new/', views.post_job, name='post_job'),
    path('market/job/<int:pk>/', views.job_detail, name='job_detail'),
    path('market/job/<int:pk>/like/', views.toggle_job_like, name='toggle_job_like'),
    path('market/job/<int:pk>/bookmark/', views.toggle_job_bookmark, name='toggle_job_bookmark'),
    path('market/my-jobs/', views.my_jobs, name='my_jobs'),
]