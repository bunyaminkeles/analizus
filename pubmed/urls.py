from django.urls import path
from . import views

app_name = 'pubmed'

urlpatterns = [
    path('', views.pubmed_landing, name='landing'),
    path('status/<uuid:job_id>/', views.pubmed_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.pubmed_send_demo_email, name='send_demo_email'),
    path('cancel/<uuid:job_id>/', views.pubmed_cancel, name='cancel'),
    path('download-excel/<uuid:job_id>/', views.pubmed_download_excel, name='download_excel'),
    path('download-txt/<uuid:job_id>/', views.pubmed_download_txt, name='download_txt'),
]
