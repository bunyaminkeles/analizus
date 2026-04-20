from django.contrib import admin
from .models import IstatistikJob


@admin.register(IstatistikJob)
class IstatistikJobAdmin(admin.ModelAdmin):
    list_display = ('tool', 'user', 'status', 'is_demo', 'created_at')
    list_filter = ('tool', 'status', 'is_demo')
    search_fields = ('user__username', 'original_filename')
    readonly_fields = ('id', 'created_at', 'completed_at', 'result_data', 'pdf_url', 'error_message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
