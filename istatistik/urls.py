from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'istatistik'

# (url_slug, view_fn, name, has_status) — url_slug bazı araçlarda kısa çizgili
# (mann-whitney), name'de alt çizgi kullanılır ({% url 'istatistik:mann_whitney' %}
# — polling/form JS'i hâlâ bu isimlere bağlı). url_slug, urls_analiz.py'deki
# _SLUG_MAP ve forum/sitemaps.py'deki IstatistikSitemap ile senkron tutulmalı.
_TOOLS = [
    ('cronbach', views.cronbach_landing, 'cronbach', True),
    ('normallik', views.normallik_landing, 'normallik', True),
    ('betimsel', views.betimsel_landing, 'betimsel', True),
    ('korelasyon', views.korelasyon_landing, 'korelasyon', True),
    ('orneklem', views.orneklem_landing, 'orneklem', False),
    ('ttesti', views.ttesti_landing, 'ttesti', True),
    ('anova', views.anova_landing, 'anova', True),
    ('mann-whitney', views.mann_whitney_landing, 'mann_whitney', True),
    ('kruskal-wallis', views.kruskal_wallis_landing, 'kruskal_wallis', True),
    ('ki-kare', views.ki_kare_landing, 'ki_kare', True),
    ('lineer-regresyon', views.lineer_regresyon_landing, 'lineer_regresyon', True),
    ('lojistik-regresyon', views.lojistik_regresyon_landing, 'lojistik_regresyon', True),
    ('afa', views.afa_landing, 'afa', True),
    ('wilcoxon', views.wilcoxon_landing, 'wilcoxon', True),
    ('friedman', views.friedman_landing, 'friedman', True),
    ('tekrarli-anova', views.tekrarli_anova_landing, 'tekrarli_anova', True),
    ('karar-agaci', views.karar_agaci_landing, 'karar_agaci', True),
    ('svm', views.svm_landing, 'svm', True),
]


def _analiz_entry(view_fn, slug):
    """GET isteğini kalıcı olarak /analiz/<slug>/'e yönlendirir (SEO — /istatistik/
    ile /analiz/ arasındaki içerik ikizliğini gidermek için). POST (analiz gönderimi
    — TOOL_URL/fetch hedefi hâlâ bu isme bağlı) view_fn'e değişmeden ulaşır."""
    def _entry(request, *args, **kwargs):
        if request.method == 'GET':
            qs = request.META.get('QUERY_STRING', '')
            target = f'/analiz/{slug}/' + (f'?{qs}' if qs else '')
            return redirect(target, permanent=True)
        return view_fn(request, *args, **kwargs)
    return _entry


urlpatterns = []
for _slug, _view, _name, _has_status in _TOOLS:
    urlpatterns.append(path(f'{_slug}/', _analiz_entry(_view, _slug), name=_name))
    if _has_status:
        urlpatterns.append(path(f'{_slug}/status/<uuid:job_id>/', views.job_status, name=f'{_name}_status'))
