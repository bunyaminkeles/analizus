from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),

    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/like/', views.blog_like, name='blog_like'),

    path('register/', views.register, name='register'),
    
    # Profil
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    
    # Mesajlaşma
    path('inbox/', views.inbox, name='inbox'),
    path('send-message/<str:username>/', views.send_message, name='send_message'),
    path('api/chat/<str:username>/poll/', views.api_chat_poll, name='api_chat_poll'),
    path('api/inbox/poll/', views.api_inbox_poll, name='api_inbox_poll'),

    # Araçlar
    path('hangi-test/', views.hangi_test, name='hangi_test'),
    path('uzmanlar/', views.uzman_dizini, name='uzman_dizini'),

    # Çalışma Odaları
    path('odalar/', views.studyroom_list, name='studyroom_list'),
    path('odalar/ac/', views.studyroom_create, name='studyroom_create'),
    path('odalar/<slug:slug>/', views.studyroom_detail, name='studyroom_detail'),
    path('odalar/<slug:slug>/katil/', views.studyroom_join, name='studyroom_join'),
    path('odalar/<slug:slug>/poll/', views.studyroom_poll, name='studyroom_poll'),
    path('odalar/<slug:slug>/davet/', views.studyroom_invite, name='studyroom_invite'),
    path('odalar/<slug:slug>/duzenle/', views.studyroom_edit, name='studyroom_edit'),
    path('odalar/<slug:slug>/sil/', views.studyroom_delete, name='studyroom_delete'),
    path('odalar/<slug:slug>/onayla/', views.studyroom_approve, name='studyroom_approve'),

    # Forum
    path('forum/', views.forum_index, name='forum_index'),
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

    # Onboarding
    path('onboarding/', views.onboarding, name='onboarding'),

    # Admin Actions (Django admin dashboard'dan kullanılıyor)
    path('admin-actions/verify-linkedin/<int:user_id>/', views.admin_verify_linkedin, name='admin_verify_linkedin'),
    path('admin-actions/approve-story/<int:pk>/', views.dashboard_approve_story, name='dashboard_approve_story'),
    path('admin-actions/approve-review/<int:pk>/', views.dashboard_approve_review, name='dashboard_approve_review'),
    path('admin-actions/approve-donation/<int:pk>/', views.dashboard_approve_donation, name='dashboard_approve_donation'),
    path('admin-actions/mark-contact-read/<int:pk>/', views.dashboard_mark_contact_read, name='dashboard_mark_contact_read'),
    path('admin-actions/dashboard/export-csv/', views.dashboard_export_csv, name='dashboard_export_csv'),

    # Diğer
    path('search/', views.search_result, name='search'),
    path('hakkimizda/', views.about, name='about'),
    path('neden-biz/', views.neden_biz, name='neden_biz'),
    path('liderboard/', views.liderboard, name='liderboard'),
    path('nasil-calisir/', views.how_it_works, name='how_it_works'),
    path('tableau-analiz/', views.tableau_dashboard, name='tableau_dashboard'),
    path('iletisim/', views.contact, name='contact'),
    
    # Section Detail
    path('section/<int:pk>/', views.section_detail, name='section_detail'),

    # Başarı Hikayeleri
    path('success-stories/', views.success_stories, name='success_stories'),

    # Freelance Market
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
    path('my-payments/', views.my_payments, name='my_payments'),
    path('market/job/<int:pk>/promote/', views.promote_job, name='promote_job'),
    path('market/job/<int:pk>/payment-transferred/', views.mark_payment_transferred, name='mark_payment_transferred'),

    # API Endpoints (Quiz & Stories)
    path('api/quiz/random/', views.api_get_quiz_question, name='api_get_quiz_question'),
    path('api/quiz/answer/', views.api_submit_quiz_answer, name='api_submit_quiz_answer'),
    path('api/story/featured/', views.api_get_featured_story, name='api_get_featured_story'),
    path('api/widgets/rates/', api_views.widget_market_rates, name='widget_rates'),
    path('api/widgets/proposals/', api_views.widget_latest_proposals, name='widget_proposals'),
    path('api/follow/<str:username>/', api_views.toggle_follow_user, name='api_toggle_follow'),

    # Kullanıcı Arama (@mention autocomplete)
    path('api/users/search/', views.user_search_api, name='user_search_api'),

    # Bağış Sistemi
    path('api/send-support-email/', views.send_support_email, name='send_support_email'),
    path('donation/success/', views.donation_success, name='donation_success'),

    # Cron Job Endpoints (External cron services için)
    path('api/cron/daily-quiz/', api_views.cron_generate_daily_quiz, name='cron_daily_quiz'),
    path('api/cron/update-badges/', api_views.cron_update_badges_ranks, name='cron_update_badges'),
    path('api/cron/cleanup-s3/', api_views.cron_cleanup_s3_files, name='cron_cleanup_s3'),
    path('api/cron/cleanup-attachments/', api_views.cron_cleanup_attachments, name='cron_cleanup_attachments'),
    path('api/cron/health/', api_views.cron_health_check, name='cron_health'),
    path('api/admin/queue-status/', api_views.admin_queue_status, name='admin_queue_status'),

    # Admin setup (kullandıktan sonra kaldırın!)
    path('api/admin-setup/', api_views.admin_create_or_reset, name='admin_setup'),
    path('api/initial-setup/', api_views.run_initial_setup, name='initial_setup'),
]
