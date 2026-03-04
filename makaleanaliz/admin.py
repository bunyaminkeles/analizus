from django.contrib import admin
from .models import MakaleAnaliz


@admin.register(MakaleAnaliz)
class MakaleAnalizAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_query_summary', 'status', 'total_records', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'query_summary']
    readonly_fields = ['id', 'created_at', 'completed_at', 'analysis_data']
