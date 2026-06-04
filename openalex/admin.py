from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from .models import AlexOrderProxy


@admin.register(AlexOrderProxy)
class AlexOrderAdmin(ModelAdmin):
    warn_unsaved_changes = True
    compressed_fields = True
    list_display = ('id_short', 'user', 'abstract_count', 'total_price', 'status',
                    'results_email_sent', 'created_at')
    list_filter = ('status', 'results_email_sent')
    search_fields = ('user__username',)
    readonly_fields = ('id', 'status', 'created_at', 'updated_at', 'approved_at',
                       'results_email_sent_at')
    ordering = ('-created_at',)
    actions = ['approve_and_send_email']

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    @admin.action(description='Onayla ve Tam Rapor Emailini Gönder')
    def approve_and_send_email(self, request, queryset):
        from openalex.services.job_runner import send_order_results_email
        sent_count = 0
        for order in queryset.filter(
            status__in=['pending_payment', 'payment_review', 'approved', 'processing']
        ):
            order.status = 'approved'
            order.approved_at = timezone.now()
            order.save(update_fields=['status', 'approved_at'])
            success = send_order_results_email(order)
            if success:
                sent_count += 1
        self.message_user(request, f'{sent_count} siparişe tam rapor emaili gönderildi.')
