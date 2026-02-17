from django.contrib import admin, messages
from django.utils import timezone
from .models import AlexSearchJob, AlexOrder
from .services.job_runner import send_order_results_email


@admin.register(AlexSearchJob)
class AlexSearchJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at', 'demo_email_sent')
    list_filter = ('status', 'created_at', 'demo_email_sent')
    search_fields = ('user__username', 'api_query', 'id')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')
    fieldsets = (
        (None, {'fields': ('id', 'user', 'status', 'total_results', 'error_message')}),
        ('Sorgu', {'fields': ('query_parts', 'api_query')}),
        ('Dosyalar', {'fields': ('demo_file_url', 'all_results_file_url')}),
        ('Zaman', {'fields': ('created_at', 'completed_at', 'demo_email_sent')}),
    )

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(AlexOrder)
class AlexOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'search_job_id', 'status', 'abstract_count', 'total_price', 'created_at', 'approved_at', 'is_overdue')
    list_filter = ('status', 'created_at', 'approved_at')
    search_fields = ('user__username', 'search_job__id', 'payment_note', 'admin_note', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'approved_at', 'results_email_sent_at', 'search_job')
    list_select_related = ('user', 'search_job')
    actions = ['approve_and_send', 'mark_cancelled']

    fieldsets = (
        (None, {'fields': ('id', 'user', 'search_job', 'status')}),
        ('Detaylar', {'fields': ('abstract_count', 'total_price')}),
        ('Notlar', {'fields': ('payment_note', 'admin_note')}),
        ('Zaman', {'fields': ('created_at', 'updated_at', 'approved_at')}),
        ('Gönderim', {'fields': ('results_email_sent', 'results_email_sent_at')}),
    )

    def search_job_id(self, obj):
        return obj.search_job.id
    search_job_id.short_description = "Arama ID"

    def approve_and_send(self, request, queryset):
        """Seçili siparişleri onayla ve sonuçları emaile gönder."""
        sent = 0
        failed = 0
        for order in queryset.filter(status__in=['pending_payment', 'payment_review']):
            order.status = 'approved'
            order.approved_at = timezone.now()
            order.save(update_fields=['status', 'approved_at'])

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
