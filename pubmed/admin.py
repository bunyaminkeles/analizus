from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import PubMedSearchJob


@admin.register(PubMedSearchJob)
class PubMedSearchJobAdmin(ModelAdmin):
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'api_query')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"
