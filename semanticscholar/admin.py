from django.contrib import admin
from .models import SemanticSearchJob, SemanticOrder


@admin.register(SemanticSearchJob)
class SemanticSearchJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_results', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'api_query')
    readonly_fields = ('id', 'created_at', 'completed_at')


@admin.register(SemanticOrder)
class SemanticOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'abstract_count', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    readonly_fields = ('id', 'created_at', 'updated_at')
