from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SemanticSearchJob, SemanticOrder


@admin.register(SemanticSearchJob)
class SemanticSearchJobAdmin(ModelAdmin):
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'api_query')
    readonly_fields = ('id', 'created_at', 'completed_at')

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(SemanticOrder)
class SemanticOrderAdmin(ModelAdmin):
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id', 'user', 'abstract_count', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    readonly_fields = ('id', 'created_at', 'updated_at')
