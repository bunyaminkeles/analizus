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
]
