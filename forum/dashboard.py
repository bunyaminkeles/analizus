from forum.services.dashboard_service import get_dashboard_context


def dashboard_callback(request, context):
    """Unfold DASHBOARD_CALLBACK — tüm admin dashboard verisini inject eder."""
    context.update(get_dashboard_context())

    # Navigasyon paneli için link grupları
    context["nav_ekosistem"] = [
        {"label": "Kullanıcılar",     "icon": "person",             "url": "/admin/auth/user/"},
        {"label": "Profiller",        "icon": "badge",              "url": "/admin/forum/profile/"},
        {"label": "Bağışlar",         "icon": "volunteer_activism", "url": "/admin/forum/donation/"},
        {"label": "Bağış Katmanları", "icon": "layers",             "url": "/admin/forum/donationtier/"},
        {"label": "İş Ödemeleri",     "icon": "payments",           "url": "/admin/forum/jobpayment/"},
    ]
    context["nav_forum"] = [
        {"label": "Bölümler",          "icon": "grid_view",     "url": "/admin/forum/section/"},
        {"label": "Konular",           "icon": "forum",         "url": "/admin/forum/topic/"},
        {"label": "Gönderiler",        "icon": "chat_bubble",   "url": "/admin/forum/post/"},
        {"label": "Blog Yazıları",     "icon": "article",       "url": "/admin/forum/blogpost/"},
        {"label": "Blog Kategorileri", "icon": "folder",        "url": "/admin/forum/blogcategory/"},
        {"label": "Başarı Hikayeleri", "icon": "emoji_events",  "url": "/admin/forum/successstory/"},
        {"label": "Çalışma Odaları",   "icon": "meeting_room",  "url": "/admin/forum/studyroom/"},
        {"label": "Freelance İşler",   "icon": "work",          "url": "/admin/forum/freelancejob/"},
        {"label": "Rozetler",          "icon": "military_tech", "url": "/admin/forum/badge/"},
        {"label": "Quiz Soruları",     "icon": "quiz",          "url": "/admin/forum/quizquestion/"},
        {"label": "Konu Etiketleri",   "icon": "label",         "url": "/admin/forum/topictag/"},
    ]
    context["nav_analiz"] = [
        {"label": "OpenAlex İşleri",         "icon": "travel_explore",  "url": "/admin/oaipmh/alexsearchjobproxy/"},
        {"label": "TR Dizin İşleri",         "icon": "search",          "url": "/admin/oaipmh/dizinsearchjobproxy/"},
        {"label": "YÖK Tez İşleri",          "icon": "school",          "url": "/admin/oaipmh/yoktezsearchjobproxy/"},
        {"label": "OAI-PMH İşleri",          "icon": "hub",             "url": "/admin/oaipmh/oaipmhsearchjob/"},
        {"label": "Üniversiteler",           "icon": "account_balance",  "url": "/admin/oaipmh/university/"},
        {"label": "Tez Analizleri",          "icon": "biotech",         "url": "/admin/tezanaliz/tezanaliz/"},
        {"label": "Makale Analizleri",       "icon": "description",     "url": "/admin/tezanaliz/makaleanalizproxy/"},
        {"label": "Bibliometrik İşler",      "icon": "bar_chart",       "url": "/admin/tezanaliz/bibliometricjobproxy/"},
        {"label": "Bibliometrik Siparişler", "icon": "receipt_long",    "url": "/admin/tezanaliz/bibliometricorderproxy/"},
    ]
    context["nav_sistem"] = [
        {"label": "Site Ayarları",      "icon": "settings", "url": "/admin/forum/sitesettings/"},
        {"label": "İletişim Mesajları", "icon": "mail",     "url": "/admin/forum/contactmessage/"},
        {"label": "Özel Mesajlar",      "icon": "lock",     "url": "/admin/forum/privatemessage/"},
        {"label": "Gruplar",            "icon": "group",    "url": "/admin/auth/group/"},
    ]

    return context
