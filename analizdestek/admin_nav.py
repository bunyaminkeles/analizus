"""
Admin sidebar'daki "Arama & Analiz" bölümündeki çok sayıda ayrı sayfayı 2 grupta
sekmeli göstermek için paylaşılan tanımlar. Her sekme gerçek bir changelist
sayfasına link verir — hiçbir ModelAdmin'in filtre/arama/aksiyon davranışı
değişmiyor, yalnız sayfanın üstüne bir sekme çubuğu ekleniyor
(Unfold'un list_before_template hook'u ile, templates/admin/includes/group_tabs.html).
"""
from django.urls import reverse

GROUP1_TABS = [
    ("OpenAlex İşleri", "admin:oaipmh_alexsearchjobproxy_changelist"),
    ("TR Dizin İşleri", "admin:oaipmh_dizinsearchjobproxy_changelist"),
    ("YÖK Tez İşleri", "admin:oaipmh_yoktezsearchjobproxy_changelist"),
    ("YÖK Tez Üniversiteleri", "admin:yoktez_yoktezuniversite_changelist"),
    ("OAI-PMH İşleri", "admin:oaipmh_oaipmhsearchjob_changelist"),
    ("Üniversiteler", "admin:oaipmh_university_changelist"),
]

GROUP2_TABS = [
    ("Tez Analizleri", "admin:tezanaliz_tezanaliz_changelist"),
    ("Makale Analizleri", "admin:tezanaliz_makaleanalizproxy_changelist"),
    ("Bibliometrik İşler", "admin:tezanaliz_bibliometricjobproxy_changelist"),
    ("Bibliometrik Siparişler", "admin:tezanaliz_bibliometricorderproxy_changelist"),
]


class GroupTabsMixin:
    """ModelAdmin'e eklenince changelist üstünde grup sekme çubuğu gösterir."""
    group_tabs_list = []
    list_before_template = "admin/includes/group_tabs.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['group_tabs'] = [
            {"title": title, "url": reverse(url_name), "active": request.path == reverse(url_name)}
            for title, url_name in self.group_tabs_list
        ]
        return super().changelist_view(request, extra_context=extra_context)
