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
        # Tam veri çekimi (~30–60 sn) istek içinde değil arka plan kuyruğunda: veri → TXT → S3 → e-posta.
        # 'processing' = kuyrukta/çalışıyor → tekrar seçilirse çift gönderim olmasın diye atlanır.
        # Hata olursa iş siparişi 'approved'a döndürür ve admin notuna yazar (yeniden çalıştırılabilir).
        from openalex.services.job_runner import run_order_job
        queued = 0
        for order in queryset.filter(
            status__in=['pending_payment', 'payment_review', 'approved']
        ):
            order.status = 'processing'
            order.approved_at = timezone.now()
            order.save(update_fields=['status', 'approved_at'])
            run_order_job(order.id)
            queued += 1
        self.message_user(request, f'{queued} sipariş kuyruğa alındı; veri hazırlanınca tam rapor emaili '
                                   f'otomatik gönderilecek (hata olursa sipariş "Onaylandı"ya döner, Admin Notu\'na bakın).')
