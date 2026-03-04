from django.contrib import admin
from .models import TezAnaliz


@admin.register(TezAnaliz)
class TezAnalizAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_query_summary', 'status', 'total_records', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'tez_ad', 'metin']
    readonly_fields = ['id', 'created_at', 'completed_at', 'records', 'analysis_data']
