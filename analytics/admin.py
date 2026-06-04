import json
from datetime import date, timedelta

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin

from .models import PageView, PageViewSummary


@admin.register(PageView)
class PageViewAdmin(ModelAdmin):
    list_display = ['timestamp', 'get_username', 'tab_name', 'path']
    search_fields = ['user__username', 'user__email', 'tab_name', 'path']
    list_filter = ['tab_name']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    ordering = ['-timestamp']
    list_select_related = True

    def get_username(self, obj):
        chart_url = reverse('admin:analytics_grafik') + f'?user={obj.user.username}'
        return format_html('<a href="{}" title="Grafiği Gör">{}</a>', chart_url, obj.user.username)
    get_username.short_description = 'Kullanıcı'
    get_username.admin_order_field = 'user__username'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('grafik/', self.admin_site.admin_view(self.chart_view), name='analytics_grafik'),
        ]
        return extra + urls

    def chart_view(self, request):
        today = date.today()
        cutoff = today - timedelta(days=6)

        username = request.GET.get('user', '').strip()
        qs = PageView.objects.filter(timestamp__date__gte=cutoff)
        if username:
            qs = qs.filter(user__username=username)

        top_pages = list(
            qs.values('tab_name')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )

        daily = list(
            qs.values('timestamp__date')
            .annotate(total=Count('id'))
            .order_by('timestamp__date')
        )
        for row in daily:
            row['timestamp__date'] = str(row['timestamp__date'])

        top_users = []
        if not username:
            top_users = list(
                qs.values('user__username')
                .annotate(total=Count('id'))
                .order_by('-total')[:10]
            )

        # Kullanıcı bazlı sayfa dağılımı (kullanıcı filtrelendiğinde göster)
        user_pages = []
        if username:
            user_pages = list(
                qs.values('tab_name')
                .annotate(total=Count('id'))
                .order_by('-total')
            )

        context = {
            **self.admin_site.each_context(request),
            'title': f'Navigasyon Grafiği — {username}' if username else 'Kullanıcı Navigasyon Analizi',
            'top_pages_json': json.dumps(top_pages, cls=DjangoJSONEncoder),
            'daily_json': json.dumps(daily, cls=DjangoJSONEncoder),
            'top_users_json': json.dumps(top_users, cls=DjangoJSONEncoder),
            'user_pages_json': json.dumps(user_pages, cls=DjangoJSONEncoder),
            'username': username,
            'date_range': f'{cutoff} — {today}',
        }
        return render(request, 'admin/analytics/chart.html', context)


@admin.register(PageViewSummary)
class PageViewSummaryAdmin(ModelAdmin):
    list_display = ['date', 'tab_name', 'visit_count', 'unique_users', 'path']
    list_filter = ['tab_name']
    date_hierarchy = 'date'
    ordering = ['-date', '-visit_count']
    list_per_page = 50
    search_fields = ['tab_name', 'path']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
