from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import api_views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),

    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/like/', views.blog_like, name='blog_like'),

    # Profil
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    
    # Mesajlaşma
    path('inbox/', views.inbox, name='inbox'),
    path('send-message/<str:username>/', views.send_message, name='send_message'),
    path('api/chat/<str:username>/poll/', views.api_chat_poll, name='api_chat_poll'),
    path('api/inbox/poll/', views.api_inbox_poll, name='api_inbox_poll'),
    path('api/message/<int:message_id>/edit/', views.api_edit_message, name='api_edit_message'),
    path('api/message/<int:message_id>/delete/', views.api_delete_message, name='api_delete_message'),
    path('api/chat/<str:username>/delete-conversation/', views.api_delete_conversation, name='api_delete_conversation'),
    path('api/room-post/<int:post_id>/edit/', views.api_edit_room_post, name='api_edit_room_post'),
    path('api/room-post/<int:post_id>/delete/', views.api_delete_room_post, name='api_delete_room_post'),

    # Araçlar
    path('uzmanlar/', views.uzman_dizini, name='uzman_dizini'),

    # Çalışma Odaları
    path('odalar/', views.studyroom_list, name='studyroom_list'),
    path('odalar/ac/', views.studyroom_create, name='studyroom_create'),
    path('odalar/<slug:slug>/', views.studyroom_detail, name='studyroom_detail'),
    path('odalar/<slug:slug>/katil/', views.studyroom_join, name='studyroom_join'),
    path('odalar/<slug:slug>/bekle/', views.studyroom_waitlist_join, name='studyroom_waitlist_join'),
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

    # AI Asistan (sayfa → forum/urls_i18n.py; API burada kalır — /api/ öneki
    # EmailVerificationMiddleware'de doğrulanmamış kullanıcıya da açık)
    path('api/ai/suggest/<int:topic_id>/', views.ai_suggest_answer, name='ai_suggest_answer'),
    path('api/ai/chat/', views.api_ai_chat, name='api_ai_chat'),

    # E-posta Doğrulama + Onboarding → forum/urls_i18n.py'ye taşındı (EN/DE
    # ile kaydolan kullanıcı kayıt sonrası akışta Türkçe sayfaya düşmesin)

    # Admin Actions (Django admin dashboard'dan kullanılıyor)
    path('admin-actions/verify-linkedin/<int:user_id>/', views.admin_verify_linkedin, name='admin_verify_linkedin'),
    path('admin-actions/approve-story/<int:pk>/', views.dashboard_approve_story, name='dashboard_approve_story'),
    path('admin-actions/approve-review/<int:pk>/', views.dashboard_approve_review, name='dashboard_approve_review'),
    path('admin-actions/approve-donation/<int:pk>/', views.dashboard_approve_donation, name='dashboard_approve_donation'),
    path('admin-actions/mark-contact-read/<int:pk>/', views.dashboard_mark_contact_read, name='dashboard_mark_contact_read'),
    path('admin-actions/dashboard/export-csv/', views.dashboard_export_csv, name='dashboard_export_csv'),

    # Diğer
    path('search/', views.search_result, name='search'),
    path('neden-biz/', RedirectView.as_view(url='/hakkimizda/', permanent=True)),
    path('liderboard/', views.liderboard, name='liderboard'),
    path('nasil-calisir/', views.how_it_works, name='how_it_works'),
    path('tableau-analiz/', views.tableau_dashboard, name='tableau_dashboard'),

    # Section Detail
    path('section/<int:pk>/', views.section_detail, name='section_detail'),

    # Başarı Hikayeleri
    path('success-stories/', views.success_stories, name='success_stories'),

    # Eski /jobs/ URL'lerini /market/ 'e yönlendir (geriye dönük uyumluluk)
    path('jobs/', RedirectView.as_view(url='/market/', permanent=True)),
    path('jobs/<int:pk>/', RedirectView.as_view(pattern_name='job_detail', permanent=True)),

    # Freelance Market — market/* path'leri forum/urls_i18n.py'de (çok dilli arayüz)
    path('my-payments/', views.my_payments, name='my_payments'),

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
    path('donation/<int:pk>/transferred/', views.mark_donation_transferred, name='mark_donation_transferred'),

    # Cron Job Endpoints (External cron services için)
    path('api/cron/cleanup-s3/', api_views.cron_cleanup_s3_files, name='cron_cleanup_s3'),
    path('api/cron/cleanup-attachments/', api_views.cron_cleanup_attachments, name='cron_cleanup_attachments'),
    path('api/cron/cleanup-pageviews/', api_views.cron_cleanup_pageviews, name='cron_cleanup_pageviews'),
    path('api/cron/cleanup-session-datasets/', api_views.cron_cleanup_session_datasets, name='cron_cleanup_session_datasets'),
    path('api/cron/health/', api_views.cron_health_check, name='cron_health'),
    path('api/cron/process-account-deletions/', api_views.cron_process_account_deletions, name='cron_process_account_deletions'),
    path('api/admin/queue-status/', api_views.admin_queue_status, name='admin_queue_status'),

    # Admin setup (kullandıktan sonra kaldırın!)
    path('api/admin-setup/', api_views.admin_create_or_reset, name='admin_setup'),
    path('api/initial-setup/', api_views.run_initial_setup, name='initial_setup'),

    # Referral (Davet) Sistemi
    path('davet/', views.referral_dashboard, name='referral_dashboard'),
    path('davet/<str:code>/', views.referral_landing, name='referral_landing'),
]
