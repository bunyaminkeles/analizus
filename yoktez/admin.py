from django.contrib import admin
from .models import YokTezSearchJob


@admin.register(YokTezSearchJob)
class YokTezSearchJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_query_summary', 'status', 'total_results', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'tez_ad', 'yazar']
    readonly_fields = ['id', 'created_at', 'completed_at', 'demo_results']

    def get_query_summary(self, obj):
        return obj.get_query_summary()
    get_query_summary.short_description = 'Sorgu Özeti'
