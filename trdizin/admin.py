from django.contrib import admin, messages
from django.utils import timezone
from .models import DizinSearchJob, DizinOrder
from .services.job_runner import send_order_results_email, delete_from_s3


@admin.register(DizinSearchJob)
class DizinSearchJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at', 'demo_email_sent')
    list_filter = ('status', 'created_at', 'demo_email_sent')
    search_fields = ('user__username', 'lucene_query', 'id')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_results', 'all_results', 'demo_file_url', 'all_results_file_url')
    fieldsets = (
        (None, {'fields': ('id', 'user', 'status', 'total_results', 'error_message')}),
        ('Sorgu', {'fields': ('query_parts', 'lucene_query')}),
        ('Dosyalar', {'fields': ('demo_file_url', 'all_results_file_url')}),
        ('Zaman', {'fields': ('created_at', 'completed_at', 'demo_email_sent')}),
    )

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = "Sorgu Özeti"


@admin.register(DizinOrder)
class DizinOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'search_job_id', 'status', 'abstract_count', 'total_price', 'created_at', 'approved_at', 'is_overdue')
    list_filter = ('status', 'created_at', 'approved_at')
    search_fields = ('user__username', 'search_job__id', 'payment_note', 'admin_note', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'approved_at', 'results_email_sent_at', 'search_job')
    list_select_related = ('user', 'search_job')
    actions = ['mark_approved', 'mark_payment_review', 'mark_cancelled', 'send_results']

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

    @admin.action(description='Seçilenleri "Onaylandı" olarak işaretle')
    def mark_approved(self, request, queryset):
        updated = queryset.update(status='approved', approved_at=timezone.now())
        self.message_user(request, f'{updated} sipariş onaylandı.', messages.SUCCESS)

    @admin.action(description='Seçilenleri "Ödeme İnceleniyor" olarak işaretle')
    def mark_payment_review(self, request, queryset):
        updated = queryset.update(status='payment_review')
        self.message_user(request, f'{updated} sipariş ödeme incelemesine alındı.', messages.INFO)

    @admin.action(description='Seçilenleri "İptal" olarak işaretle')
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} sipariş iptal edildi.', messages.WARNING)

    @admin.action(description='Seçilen siparişlerin sonuçlarını email ile gönder')
    def send_results(self, request, queryset):
        sent_count = 0
        failed_count = 0
        for order in queryset.filter(status='approved'):
            if send_order_results_email(order):
                sent_count += 1
            else:
                failed_count += 1

        if sent_count:
            self.message_user(request, f'{sent_count} siparişin sonuçları başarıyla gönderildi.', messages.SUCCESS)
        if failed_count:
            self.message_user(request, f'{failed_count} sipariş gönderilemedi.', messages.ERROR)
        if not sent_count and not failed_count:
            self.message_user(request, 'Sadece "Onaylandı" statüsündeki siparişler gönderilebilir.', messages.WARNING)

