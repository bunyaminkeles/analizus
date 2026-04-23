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
]
