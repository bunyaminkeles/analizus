from django.urls import path
from . import views

app_name = 'istatistik'

urlpatterns = [
    path('cronbach/', views.cronbach_landing, name='cronbach'),
    path('cronbach/status/<uuid:job_id>/', views.job_status, name='cronbach_status'),
    path('normallik/', views.normallik_landing, name='normallik'),
    path('normallik/status/<uuid:job_id>/', views.job_status, name='normallik_status'),
    path('betimsel/', views.betimsel_landing, name='betimsel'),
    path('betimsel/status/<uuid:job_id>/', views.job_status, name='betimsel_status'),
    path('korelasyon/', views.korelasyon_landing, name='korelasyon'),
    path('korelasyon/status/<uuid:job_id>/', views.job_status, name='korelasyon_status'),
    path('orneklem/', views.orneklem_landing, name='orneklem'),
    path('ttesti/', views.ttesti_landing, name='ttesti'),
    path('ttesti/status/<uuid:job_id>/', views.job_status, name='ttesti_status'),
    path('anova/', views.anova_landing, name='anova'),
    path('anova/status/<uuid:job_id>/', views.job_status, name='anova_status'),
    path('mann-whitney/', views.mann_whitney_landing, name='mann_whitney'),
    path('mann-whitney/status/<uuid:job_id>/', views.job_status, name='mann_whitney_status'),
    path('kruskal-wallis/', views.kruskal_wallis_landing, name='kruskal_wallis'),
    path('kruskal-wallis/status/<uuid:job_id>/', views.job_status, name='kruskal_wallis_status'),
    path('ki-kare/', views.ki_kare_landing, name='ki_kare'),
    path('ki-kare/status/<uuid:job_id>/', views.job_status, name='ki_kare_status'),
    path('lineer-regresyon/', views.lineer_regresyon_landing, name='lineer_regresyon'),
    path('lineer-regresyon/status/<uuid:job_id>/', views.job_status, name='lineer_regresyon_status'),
    path('lojistik-regresyon/', views.lojistik_regresyon_landing, name='lojistik_regresyon'),
    path('lojistik-regresyon/status/<uuid:job_id>/', views.job_status, name='lojistik_regresyon_status'),
]
