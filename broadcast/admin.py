from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import EmailBroadcast


@admin.register(EmailBroadcast)
class EmailBroadcastAdmin(ModelAdmin):
    list_display = ['created_at', 'subject', 'get_sender', 'recipient_count', 'sent_count', 'failed_count']
    list_filter = ['created_at']
    search_fields = ['subject', 'body', 'sent_by__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['sent_by', 'subject', 'body', 'recipients', 'recipient_count', 'sent_count', 'failed_count', 'created_at']
    filter_horizontal = ['recipients']

    def get_sender(self, obj):
        return obj.sent_by.username if obj.sent_by else '—'
    get_sender.short_description = 'Gönderen'
    get_sender.admin_order_field = 'sent_by__username'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
