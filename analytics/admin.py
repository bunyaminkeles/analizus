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
        chart_url = reverse('admin:analytics_grafik')
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

        qs = PageView.objects.filter(timestamp__date__gte=cutoff)

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

        top_users = list(
            qs.values('user__username')
            .annotate(total=Count('id'))
            .order_by('-total')[:20]
        )
        per_user_data = {}
        for u in top_users:
            uname = u['user__username']
            u_qs = qs.filter(user__username=uname)
            u_pages = list(u_qs.values('tab_name').annotate(total=Count('id')).order_by('-total')[:10])
            u_daily = list(u_qs.values('timestamp__date').annotate(total=Count('id')).order_by('timestamp__date'))
            for r in u_daily:
                r['timestamp__date'] = str(r['timestamp__date'])
            per_user_data[uname] = {'pages': u_pages, 'daily': u_daily}

        context = {
            **self.admin_site.each_context(request),
            'title': 'Kullanıcı Navigasyon Analizi',
            'top_pages_json': json.dumps(top_pages, cls=DjangoJSONEncoder),
            'daily_json': json.dumps(daily, cls=DjangoJSONEncoder),
            'top_users_json': json.dumps(top_users, cls=DjangoJSONEncoder),
            'per_user_data_json': json.dumps(per_user_data, cls=DjangoJSONEncoder),
            'date_range': f'{cutoff} — {today}',
        }
        return render(request, 'admin/analytics/chart.html', context)


@admin.register(PageViewSummary)
class PageViewSummaryAdmin(ModelAdmin):
    list_display = ['date', 'get_username', 'tab_name', 'visit_count', 'path']
    list_filter = ['tab_name']
    date_hierarchy = 'date'
    ordering = ['-date', '-visit_count']
    list_per_page = 50
    search_fields = ['user__username', 'tab_name', 'path']
    list_select_related = True

    def get_username(self, obj):
        if obj.user:
            chart_url = reverse('admin:analytics_grafik') + f'?user={obj.user.username}'
            return format_html('<a href="{}" title="Grafiği Gör">{}</a>', chart_url, obj.user.username)
        return '—'
    get_username.short_description = 'Kullanıcı'
    get_username.admin_order_field = 'user__username'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
