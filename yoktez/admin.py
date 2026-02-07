from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import TezSearchJob, TezOrder


@admin.register(TezSearchJob)
class TezSearchJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'konu', 'keywords_display', 'status', 'total_results', 'demo_email_sent', 'created_at']
    list_filter = ['status', 'demo_email_sent', 'created_at']
    search_fields = ['konu', 'user__username', 'user__email']
    readonly_fields = ['id', 'user', 'demo_results', 'all_results', 'created_at', 'completed_at']

    def keywords_display(self, obj):
        return ', '.join(obj.keywords)
    keywords_display.short_description = 'Anahtar Kelimeler'


@admin.register(TezOrder)
class TezOrderAdmin(admin.ModelAdmin):
    list_display = ['order_short_id', 'user', 'konu_display', 'abstract_count', 'total_price', 'status', 'results_email_sent', 'created_at']
    list_filter = ['status', 'results_email_sent', 'created_at']
    search_fields = ['user__username', 'user__email', 'search_job__konu']
    readonly_fields = ['id', 'user', 'search_job', 'abstract_count', 'total_price', 'created_at', 'updated_at', 'results_email_sent', 'results_email_sent_at']
    actions = ['approve_and_send', 'mark_cancelled']

    def order_short_id(self, obj):
        return f"#{str(obj.id)[:8]}"
    order_short_id.short_description = 'Sipariş No'

    def konu_display(self, obj):
        return obj.search_job.konu
    konu_display.short_description = 'Konu'

    def approve_and_send(self, request, queryset):
        """Seçili siparişleri onayla ve sonuçları emaile gönder."""
        from .services.job_runner import send_order_results_email

        sent = 0
        failed = 0
        for order in queryset.filter(status__in=['pending_payment', 'payment_review']):
            order.status = 'approved'
            order.approved_at = timezone.now()
            order.save(update_fields=['status', 'approved_at'])

            # Sonuçları email ile gönder
            order.status = 'processing'
            order.save(update_fields=['status'])

            success = send_order_results_email(order)
            if success:
                sent += 1
            else:
                failed += 1

        if sent:
            messages.success(request, f'{sent} sipariş onaylandı ve sonuçlar gönderildi.')
        if failed:
            messages.error(request, f'{failed} sipariş için email gönderilemedi.')

    approve_and_send.short_description = "Onayla ve sonuçları emaile gönder"

    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status='completed').update(status='cancelled')
        messages.warning(request, f'{updated} sipariş iptal edildi.')
    mark_cancelled.short_description = "İptal et"
