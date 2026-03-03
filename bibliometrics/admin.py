from django.contrib import admin
from django.utils.html import format_html
from .models import BibliometricJob, BibliometricOrder
from .services.job_runner import send_order_results_email


@admin.register(BibliometricJob)
class BibliometricJobAdmin(admin.ModelAdmin):
    list_display = ('id_short', 'user', 'original_filename', 'file_format',
                    'total_records', 'status', 'demo_email_sent', 'created_at')
    list_filter = ('status', 'file_format', 'demo_email_sent')
    search_fields = ('user__username', 'original_filename')
    readonly_fields = ('id', 'created_at', 'completed_at', 'demo_pdf_link', 'full_pdf_link')
    ordering = ('-created_at',)

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def demo_pdf_link(self, obj):
        if obj.demo_pdf_url:
            return format_html('<a href="{}" target="_blank">Demo PDF İndir</a>', obj.demo_pdf_url)
        return '-'
    demo_pdf_link.short_description = 'Demo PDF'

    def full_pdf_link(self, obj):
        if obj.full_pdf_url:
            return format_html('<a href="{}" target="_blank">Tam Rapor PDF İndir</a>', obj.full_pdf_url)
        return '-'
    full_pdf_link.short_description = 'Tam Rapor PDF'


@admin.register(BibliometricOrder)
class BibliometricOrderAdmin(admin.ModelAdmin):
    list_display = ('id_short', 'user', 'job_filename', 'total_price',
                    'status', 'results_email_sent', 'created_at')
    list_filter = ('status', 'results_email_sent')
    search_fields = ('user__username', 'job__original_filename')
    readonly_fields = ('id', 'created_at', 'updated_at', 'approved_at',
                       'results_email_sent_at')
    ordering = ('-created_at',)
    actions = ['approve_and_send_email']

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def job_filename(self, obj):
        return obj.job.original_filename
    job_filename.short_description = 'Dosya'

    @admin.action(description='Onayla ve Tam Rapor Emailini Gönder')
    def approve_and_send_email(self, request, queryset):
        from django.utils import timezone

        sent_count = 0
        for order in queryset:
            if order.status in ('pending_payment', 'payment_review', 'approved', 'processing'):
                order.status = 'approved'
                order.approved_at = timezone.now()
                order.save(update_fields=['status', 'approved_at'])

                success = send_order_results_email(str(order.id))
                if success:
                    sent_count += 1

        self.message_user(request, f'{sent_count} siparişe tam rapor emaili gönderildi.')
