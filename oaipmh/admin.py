from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import University, OAIPMHSearchJob, YokTezSearchJobProxy
from openalex.models import AlexSearchJobProxy
from trdizin.models import DizinSearchJobProxy
from analizdestek.admin_nav import GroupTabsMixin, GROUP1_TABS


@admin.register(University)
class UniversityAdmin(GroupTabsMixin, ModelAdmin):
    group_tabs_list = GROUP1_TABS
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ['name', 'domain', 'oai_url', 'is_active', 'last_checked_at', 'last_result_display', 'flagged_for_review']
    list_filter = ['is_active', 'flagged_for_review']
    search_fields = ['name', 'domain']
    list_editable = ['is_active']

    def last_result_display(self, obj):
        if obj.last_result_count is None:
            return '—'
        if obj.last_result_count < 0:
            return '🔌 Bağlantı Hatası'
        return obj.last_result_count
    last_result_display.short_description = "Son Test Sonucu"


@admin.register(OAIPMHSearchJob)
class OAIPMHSearchJobAdmin(GroupTabsMixin, ModelAdmin):
    group_tabs_list = GROUP1_TABS
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ['id', 'user', 'search_type', 'get_query_summary', 'status', 'total_results', 'created_at']
    list_filter = ['status', 'search_type']
    search_fields = ['user__username', 'keyword']
    readonly_fields = ['id', 'created_at', 'completed_at', 'demo_results', 'all_results']
    raw_id_fields = ['user', 'university']

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(user__is_staff=True)
        from forum.models import SiteSettings
        haric_grup = SiteSettings.load().navigasyon_haric_grup
        if haric_grup:
            qs = qs.exclude(user__groups=haric_grup)
        return qs


@admin.register(AlexSearchJobProxy)
class AlexSearchJobProxyAdmin(GroupTabsMixin, ModelAdmin):
    group_tabs_list = GROUP1_TABS
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'api_query')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(user__is_staff=True)
        from forum.models import SiteSettings
        haric_grup = SiteSettings.load().navigasyon_haric_grup
        if haric_grup:
            qs = qs.exclude(user__groups=haric_grup)
        return qs


@admin.register(DizinSearchJobProxy)
class DizinSearchJobProxyAdmin(GroupTabsMixin, ModelAdmin):
    group_tabs_list = GROUP1_TABS
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'lucene_query')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(user__is_staff=True)
        from forum.models import SiteSettings
        haric_grup = SiteSettings.load().navigasyon_haric_grup
        if haric_grup:
            qs = qs.exclude(user__groups=haric_grup)
        return qs


@admin.register(YokTezSearchJobProxy)
class YokTezSearchJobProxyAdmin(GroupTabsMixin, ModelAdmin):
    group_tabs_list = GROUP1_TABS
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'tez_ad', 'yazar')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(user__is_staff=True)
        from forum.models import SiteSettings
        haric_grup = SiteSettings.load().navigasyon_haric_grup
        if haric_grup:
            qs = qs.exclude(user__groups=haric_grup)
        return qs
