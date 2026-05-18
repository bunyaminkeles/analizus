from django.urls import path
from . import views

app_name = 'yoktez'

urlpatterns = [
    path('', views.yoktez_landing, name='landing'),
    path('status/<uuid:job_id>/', views.yoktez_job_status, name='job_status'),
    path('download/<uuid:job_id>/', views.yoktez_download, name='download'),
    path('download-excel/<uuid:job_id>/', views.yoktez_download_excel, name='download_excel'),
    path('send-demo/<uuid:job_id>/', views.yoktez_send_demo_email, name='send_demo'),
    path('cancel/<uuid:job_id>/', views.yoktez_cancel, name='cancel'),
    # Tez analizi (tezanaliz app'ten birleştirildi)
    path('analiz/<uuid:yok_job_id>/', views.create_analiz, name='create_analiz'),
    path('analiz-status/<uuid:job_id>/', views.analiz_status, name='analiz_status'),
    path('sonuc/<uuid:job_id>/', views.analiz_results, name='analiz_results'),
]
