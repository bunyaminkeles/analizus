from django.contrib import admin
from .models import University, OAIPMHSearchJob, YokTezSearchJobProxy
from openalex.models import AlexSearchJobProxy
from trdizin.models import DizinSearchJobProxy


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'oai_url', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'domain']
    list_editable = ['is_active']


@admin.register(OAIPMHSearchJob)
class OAIPMHSearchJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'search_type', 'get_query_summary', 'status', 'total_results', 'created_at']
    list_filter = ['status', 'search_type']
    search_fields = ['user__username', 'keyword']
    readonly_fields = ['id', 'created_at', 'completed_at', 'demo_results', 'all_results']
    raw_id_fields = ['user', 'university']

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(AlexSearchJobProxy)
class AlexSearchJobProxyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'api_query')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(DizinSearchJobProxy)
class DizinSearchJobProxyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'lucene_query')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(YokTezSearchJobProxy)
class YokTezSearchJobProxyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'tez_ad', 'yazar')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"
