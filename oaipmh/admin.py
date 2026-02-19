from django.contrib import admin
from .models import University, OAIPMHSearchJob, OAIPMHOrder


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'oai_url', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'domain']
    list_editable = ['is_active']


@admin.register(OAIPMHSearchJob)
class OAIPMHSearchJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'search_type', 'get_query_summary', 'status', 'total_results', 'created_at']
    list_filter = ['status', 'search_type']
    search_fields = ['user__username', 'keyword']
    readonly_fields = ['id', 'created_at', 'completed_at', 'demo_results', 'all_results']
    raw_id_fields = ['user', 'university']


@admin.register(OAIPMHOrder)
class OAIPMHOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'abstract_count', 'total_price', 'status', 'results_email_sent', 'created_at']
    list_filter = ['status', 'results_email_sent']
    search_fields = ['user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'search_job']

    actions = ['send_results_email']

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = OAIPMHOrder.objects.filter(pk=obj.pk).values_list('status', flat=True).first()
        super().save_model(request, obj, form, change)
        # Status yeni 'approved' yapıldıysa ve henüz mail gönderilmediyse otomatik gönder
        if obj.status == 'approved' and old_status != 'approved' and not obj.results_email_sent:
            from .services.job_runner import send_order_results_email
            if send_order_results_email(obj):
                self.message_user(request, f"Sonuçlar {obj.user.email} adresine gönderildi.")
            else:
                self.message_user(request, "Email gönderilemedi — loglara bakın.", level='error')

    def send_results_email(self, request, queryset):
        from .services.job_runner import send_order_results_email
        sent = 0
        for order in queryset.filter(results_email_sent=False):
            if send_order_results_email(order):
                sent += 1
        self.message_user(request, f"{sent} sipariş için sonuçlar gönderildi.")
    send_results_email.short_description = "Seçili siparişlerin sonuçlarını gönder"
