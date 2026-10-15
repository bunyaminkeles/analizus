import json
from collections import Counter, defaultdict
from datetime import date, timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Sum, Min, Max
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse
from unfold.admin import ModelAdmin

from .models import PageView, PageViewSummary

# Navigasyon akışı: ardışık iki ziyaret arası bu süreyi aşarsa yeni oturum sayılır
SESSION_GAP_MINUTES = 30
# Akışta gösterilen en fazla ham kayıt (en yeniler)
FLOW_LIMIT = 300
# "Şu An Aktif" penceresi — Profile.is_online ile aynı eşik (forum/models.py)
ACTIVE_NOW_MINUTES = 5
# Zorunlu yönlendirme/huni adımları — organik "ilgi" değil (EmailVerificationMiddleware
# doğrulanmamış kullanıcıyı her tıklamada verification-pending'e atıyor; Onboarding her yeni
# üyenin e-posta doğrulaması sonrası tek seferlik zorunlu geçişi) — "En Çok Ziyaret Edilen
# Sayfalar"da gürültü yaratıyor, o yüzden yalnız oradan hariç tutuluyor (ham log ve kullanıcı
# bazlı Navigasyon Akışı etkilenmez, destek/debug amaçlı orada görünmeye devam eder)
_TRANSIT_TAB_NAMES = ('Onboarding', '/verification-pending/')


def user_analysis_link(user):
    """Listelerdeki kullanıcı adı → o kişinin davranış analizi (Navigasyon Grafiği ?user=)."""
    url = reverse('admin:analytics_grafik') + '?' + urlencode({'user': user.username})
    return format_html('<a href="{}" title="Davranış analizini aç">{}</a>', url, user.username)


def build_sessions(views):
    """Kronolojik ziyaretleri oturumlara böler; en yeni oturum başta."""
    gap = timedelta(minutes=SESSION_GAP_MINUTES)
    sessions = []
    for v in views:
        if not sessions or v['timestamp'] - sessions[-1]['end'] > gap:
            sessions.append({'start': v['timestamp'], 'steps': []})
        sessions[-1]['steps'].append(v)
        sessions[-1]['end'] = v['timestamp']
    sessions.reverse()
    return sessions


def top_transitions(sessions, n=8):
    """Oturum içi bölümler arası geçişler (aynı bölüm içinde gezinme sayılmaz), en sık n tanesi."""
    counter = Counter()
    for s in sessions:
        steps = s['steps']
        for a, b in zip(steps, steps[1:]):
            if a['tab_name'] != b['tab_name']:
                counter[(a['tab_name'], b['tab_name'])] += 1
    return [{'source': a, 'target': b, 'count': c} for (a, b), c in counter.most_common(n)]


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
        return user_analysis_link(obj.user)
    get_username.short_description = 'Kullanıcı'
    get_username.admin_order_field = 'user__username'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('davranis-analizi/', self.admin_site.admin_view(self.behavior_analysis_view), name='analytics_behavior_analysis'),
            path('grafik/', self.admin_site.admin_view(self.chart_view), name='analytics_grafik'),
            path('aktif/', self.admin_site.admin_view(self.active_now_view), name='analytics_aktif'),
            path('arama-kelimeleri/', self.admin_site.admin_view(self.search_keywords_view), name='analytics_search_keywords'),
            path('arama-kelimeleri/detay/', self.admin_site.admin_view(self.search_keywords_detail_view), name='analytics_search_keywords_detail'),
            path('sifir-sonuc/', self.admin_site.admin_view(self.zero_results_view), name='analytics_zero_results'),
        ]
        return extra + urls

    def behavior_analysis_view(self, request):
        """
        Şu An Aktif / Navigasyon Grafiği / 0 Sonuç Aramalar / Arama Kelimeleri'ni tek sayfada
        sekme olarak birleştirir (sidebar'da az yer kaplasın diye) — her sekme, standalone
        sayfasıyla aynı context-oluşturma metodunu kullanır (_active_now_context vb.),
        böylece mantık tekrarlanmıyor. Standalone sayfalar (grafik/, aktif/ vb.) kaldırılmadı:
        user_analysis_link() ve active_now.html'deki "?user=" derin linkleri hâlâ o sayfalara
        gidiyor — kendi başına tam bir sayfa, filtre durumu daha net.
        """
        requested_user = request.GET.get('user', '').strip()
        default_tab = 'grafik' if requested_user else 'aktif'

        context = {
            **self.admin_site.each_context(request),
            'title': 'Davranış Analizi',
            'default_tab': default_tab,
            **self._active_now_context(request),
            **self._chart_context(request),
            **self._search_keywords_context(),
            **self._zero_results_context(),
        }
        return render(request, 'admin/analytics/behavior_analysis.html', context)

    def search_keywords_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'En Çok Aranan Kelimeler',
            **self._search_keywords_context(),
        }
        return render(request, 'admin/analytics/search_keywords.html', context)

    def _search_keywords_context(self):
        from forum.services.dashboard_service import get_search_keywords_chart_data

        labels_json, counts_json = get_search_keywords_chart_data()
        return {'keyword_labels_json': labels_json, 'keyword_counts_json': counts_json}

    # Kelime grafiğinde bir bara tıklayınca hangi araç/kullanıcıdan geldiğini gösterir
    _KEYWORD_TOOL_ADMIN_URL_NAME = {
        'OpenAlex': 'admin:oaipmh_alexsearchjobproxy_change',
        'TR Dizin': 'admin:oaipmh_dizinsearchjobproxy_change',
        'Semantic Scholar': 'admin:semanticscholar_semanticsearchjob_change',
        'PubMed': 'admin:pubmed_pubmedsearchjob_change',
        'YÖK Tez': 'admin:oaipmh_yoktezsearchjobproxy_change',
        'OAI-PMH': 'admin:oaipmh_oaipmhsearchjob_change',
    }

    def search_keywords_detail_view(self, request):
        from forum.services.dashboard_service import get_jobs_for_keyword

        keyword = request.GET.get('keyword', '').strip()
        jobs = get_jobs_for_keyword(keyword) if keyword else []
        results = []
        for j in jobs:
            url_name = self._KEYWORD_TOOL_ADMIN_URL_NAME.get(j['tool'])
            try:
                admin_url = reverse(url_name, args=[j['job_id']]) if url_name else None
            except Exception:
                admin_url = None
            results.append({
                'tool': j['tool'],
                'user': j['user'],
                'created_at': j['created_at'].strftime('%d.%m.%Y %H:%M'),
                'admin_url': admin_url,
            })
        return JsonResponse({'keyword': keyword, 'results': results})

    def zero_results_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': '0 Sonuç Dönen Aramalar',
            **self._zero_results_context(),
        }
        return render(request, 'admin/analytics/zero_results.html', context)

    def _zero_results_context(self):
        from forum.services.dashboard_service import get_zero_result_summary

        summary = get_zero_result_summary(30)
        try:
            from yoktez.models import YokTezUniversite
            flagged_universities = YokTezUniversite.objects.filter(flagged_for_review=True).order_by('name')
        except Exception:
            flagged_universities = []

        try:
            from oaipmh.models import University
            flagged_oaipmh_universities = University.objects.filter(flagged_for_review=True).order_by('name')
        except Exception:
            flagged_oaipmh_universities = []

        return {
            'zero_result_summary': summary,
            'yoktez_flagged_universities': flagged_universities,
            'flagged_oaipmh_universities': flagged_oaipmh_universities,
        }

    def active_now_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Şu An Aktif',
            **self._active_now_context(request),
        }
        return render(request, 'admin/analytics/active_now.html', context)

    def _active_now_context(self, request):
        """
        Son ACTIVE_NOW_MINUTES dakikada aktif kullanıcılar — Profile.last_seen üzerinden (profil kartındaki
        yeşil "çevrimiçi" noktasıyla aynı sinyal). last_seen HER girişli istekte güncellenir (API/WebSocket/
        polling dahil, LastSeenMiddleware); PageView ise yalnız gerçek sayfa navigasyonunda yazılır
        (PageViewMiddleware, /api/ /ws/ /admin/ vb. hariç) — bu yüzden yalnız PageView kullanmak, bir sayfada
        durup arka planda polling/WebSocket ile açık kalan kullanıcıları (yeşil nokta yanıyor ama yeni sayfa
        açmıyor) listeden düşürüyordu. Sayfa bilgisi varsa (son pencerede bir PageView kaydı varsa) eklenir,
        yoksa "—" gösterilir.
        """
        from forum.models import Profile

        cutoff = timezone.now() - timedelta(minutes=ACTIVE_NOW_MINUTES)

        recent_views = (
            PageView.objects.filter(timestamp__gte=cutoff)
            .order_by('user_id', '-timestamp')
            .values('user_id', 'tab_name', 'path')
        )
        latest_page_by_user = {}
        for row in recent_views:
            if row['user_id'] not in latest_page_by_user:
                latest_page_by_user[row['user_id']] = row

        active_profiles = (
            Profile.objects.filter(last_seen__gte=cutoff)
            .select_related('user')
            .order_by('-last_seen')
        )

        active_users = []
        for profile in active_profiles:
            page = latest_page_by_user.get(profile.user_id)
            active_users.append({
                'user__username': profile.user.username,
                'tab_name': page['tab_name'] if page else None,
                'path': page['path'] if page else None,
                'timestamp': profile.last_seen,
            })

        return {
            'active_users': active_users,
            'active_minutes': ACTIVE_NOW_MINUTES,
            'now': timezone.now(),
        }

    def chart_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Kullanıcı Navigasyon Analizi',
            **self._chart_context(request),
        }
        return render(request, 'admin/analytics/chart.html', context)

    def _chart_context(self, request):
        """
        Ham loglar (PageView) 5 günden eskisi cleanup_pageviews tarafından
        PageViewSummary'e taşınıp silindiği için, tüm geçmişi göstermek adına
        burada iki kaynak da birleştiriliyor: son ~6 gün ham'dan, öncesi
        özet'ten okunuyor. Aksi halde grafik yalnızca son birkaç günü gösterir.

        ?start=&end= (YYYY-MM-DD) üstteki 3 grafiği (top sayfalar, günlük
        trend, en aktif kullanıcılar) seçilen aralığa daraltır. Navigasyon
        akışı (oturum detayı) ham verinin fiziksel saklama penceresiyle
        (son 6 gün) sınırlı olduğu için bu filtreden etkilenmez.
        """
        today = date.today()
        cutoff = today - timedelta(days=6)

        flow_qs = PageView.objects.filter(timestamp__date__gte=cutoff)

        earliest = PageViewSummary.objects.aggregate(m=Min('date'))['m']
        range_start_default = earliest if earliest and earliest < cutoff else cutoff

        def parse_date(value):
            try:
                return date.fromisoformat(value) if value else None
            except ValueError:
                return None

        start_param = request.GET.get('start', '').strip()
        end_param = request.GET.get('end', '').strip()
        range_start = parse_date(start_param) or range_start_default
        range_end = parse_date(end_param) or today
        if range_start > range_end:
            range_start, range_end = range_end, range_start

        recent_qs = PageView.objects.filter(timestamp__date__gte=range_start, timestamp__date__lte=range_end)
        summary_qs = PageViewSummary.objects.filter(date__gte=range_start, date__lte=range_end)

        # Navigasyon Grafiği'nden admin'de seçilen grup (iç ekip vb.) de staff ile aynı mantıkla
        # hariç tutulur — bkz. SiteSettings.navigasyon_haric_grup
        from forum.models import SiteSettings
        haric_grup = SiteSettings.load().navigasyon_haric_grup

        def _exclude_internal(qs):
            qs = qs.exclude(user__is_staff=True)
            if haric_grup:
                qs = qs.exclude(user__groups=haric_grup)
            return qs

        def top_n(field, n, extra_filter=None, exclude_staff=False, extra_exclude=None):
            totals = defaultdict(int)
            rqs = _exclude_internal(recent_qs) if exclude_staff else recent_qs
            sqs = _exclude_internal(summary_qs) if exclude_staff else summary_qs
            rqs = rqs.filter(**extra_filter) if extra_filter else rqs
            sqs = sqs.filter(**extra_filter) if extra_filter else sqs
            if extra_exclude:
                rqs = rqs.exclude(**extra_exclude)
                sqs = sqs.exclude(**extra_exclude)
            for row in rqs.values(field).annotate(total=Count('id')):
                if row[field]:
                    totals[row[field]] += row['total']
            for row in sqs.values(field).annotate(total=Sum('visit_count')):
                if row[field]:
                    totals[row[field]] += row['total'] or 0
            return [{field: k, 'total': v} for k, v in sorted(totals.items(), key=lambda x: -x[1])[:n]]

        def daily_series(extra_filter=None, exclude_staff=False):
            totals = defaultdict(int)
            rqs = _exclude_internal(recent_qs) if exclude_staff else recent_qs
            sqs = _exclude_internal(summary_qs) if exclude_staff else summary_qs
            rqs = rqs.filter(**extra_filter) if extra_filter else rqs
            sqs = sqs.filter(**extra_filter) if extra_filter else sqs
            for row in rqs.values('timestamp__date').annotate(total=Count('id')):
                totals[row['timestamp__date']] += row['total']
            for row in sqs.values('date').annotate(total=Sum('visit_count')):
                totals[row['date']] += row['total'] or 0
            return [{'timestamp__date': str(d), 'total': t} for d, t in sorted(totals.items())]

        # ?user=<kullanıcı adı> → o kişinin davranış analizi (en aktif 20'de olmasa da, staff dahil)
        requested_user = request.GET.get('user', '').strip()
        selected_user = User.objects.filter(username=requested_user).first() if requested_user else None
        flt = {'user': selected_user} if selected_user else None

        # Genel görünümde (belirli kullanıcı seçilmemişken) staff hesapların test/geliştirme
        # trafiği gerçek kullanıcı davranışını gizliyor — bu yüzden yalnız o durumda hariç tutulur.
        top_pages = top_n('tab_name', 10, extra_filter=flt, exclude_staff=(flt is None),
                           extra_exclude={'tab_name__in': _TRANSIT_TAB_NAMES})
        daily = daily_series(extra_filter=flt, exclude_staff=(flt is None))
        top_users = top_n('user__username', 20, exclude_staff=True)

        user_detail = None
        if selected_user:
            views = list(
                flow_qs.filter(user=selected_user)
                .order_by('-timestamp')
                .values('timestamp', 'tab_name', 'path')[:FLOW_LIMIT]
            )
            views.reverse()  # kronolojik
            sessions = build_sessions(views)
            user_detail = {
                'total': sum(d['total'] for d in daily),
                'active_days': len(daily),
                'first_day': daily[0]['timestamp__date'] if daily else None,
                'last_day': daily[-1]['timestamp__date'] if daily else None,
                'last_visit': views[-1]['timestamp'] if views else None,
                'sessions': sessions,
                'transitions': top_transitions(sessions),
                'flow_capped': len(views) == FLOW_LIMIT,
            }

        return {
            'top_pages_json': json.dumps(top_pages, cls=DjangoJSONEncoder),
            'daily_json': json.dumps(daily, cls=DjangoJSONEncoder),
            'top_users_json': json.dumps(top_users, cls=DjangoJSONEncoder),
            'date_range': f'{range_start} — {range_end}',
            'requested_user': requested_user,
            'selected_user': selected_user,
            'user_detail': user_detail,
            'session_gap_minutes': SESSION_GAP_MINUTES,
            'flow_limit': FLOW_LIMIT,
            'requested_start': start_param,
            'requested_end': end_param,
            'range_active': bool(start_param or end_param),
            'today_iso': today.isoformat(),
        }


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
            return user_analysis_link(obj.user)
        return '—'
    get_username.short_description = 'Kullanıcı'
    get_username.admin_order_field = 'user__username'

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('grafik/', self.admin_site.admin_view(self.summary_chart_view), name='analytics_summary_grafik'),
        ]
        return extra + urls

    def summary_chart_view(self, request):
        qs = PageViewSummary.objects.all()

        top_pages = list(
            qs.values('tab_name')
            .annotate(total=Sum('visit_count'))
            .order_by('-total')[:10]
        )

        daily = list(
            qs.values('date')
            .annotate(total=Sum('visit_count'))
            .order_by('date')
        )
        for row in daily:
            row['date'] = str(row['date'])

        top_users = list(
            qs.exclude(user=None)
            .values('user__username')
            .annotate(total=Sum('visit_count'))
            .order_by('-total')[:20]
        )

        per_user_data = {}
        for u in top_users:
            uname = u['user__username']
            u_qs = qs.filter(user__username=uname)
            u_pages = list(u_qs.values('tab_name').annotate(total=Sum('visit_count')).order_by('-total')[:10])
            u_daily = list(u_qs.values('date').annotate(total=Sum('visit_count')).order_by('date'))
            for r in u_daily:
                r['date'] = str(r['date'])
            per_user_data[uname] = {'pages': u_pages, 'daily': u_daily}

        agg = qs.aggregate(
            total_visits=Sum('visit_count'),
            min_date=Min('date'),
            max_date=Max('date'),
        )
        unique_users = qs.exclude(user=None).values('user').distinct().count()
        unique_pages = qs.values('path').distinct().count()

        date_range = ''
        if agg['min_date'] and agg['max_date']:
            date_range = f'{agg["min_date"]} — {agg["max_date"]}'

        context = {
            **self.admin_site.each_context(request),
            'title': 'Ziyaret Özeti Grafiği',
            'top_pages_json': json.dumps(top_pages, cls=DjangoJSONEncoder),
            'daily_json': json.dumps(daily, cls=DjangoJSONEncoder),
            'top_users_json': json.dumps(top_users, cls=DjangoJSONEncoder),
            'per_user_data_json': json.dumps(per_user_data, cls=DjangoJSONEncoder),
            'total_visits': agg['total_visits'] or 0,
            'unique_users': unique_users,
            'unique_pages': unique_pages,
            'date_range': date_range,
        }
        return render(request, 'admin/analytics/summary_chart.html', context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
