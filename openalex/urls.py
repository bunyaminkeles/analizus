from django.urls import path
from . import views

app_name = 'openalex'

urlpatterns = [
    path('', views.openalex_landing, name='landing'),
    path('status/<uuid:job_id>/', views.openalex_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.openalex_send_demo_email, name='send_demo_email'),
    path('cancel/<uuid:job_id>/', views.openalex_cancel, name='cancel'),
    path('download-excel/<uuid:job_id>/', views.openalex_download_excel, name='download_excel'),
    path('siparis/<uuid:job_id>/', views.openalex_order_page, name='order_page'),
]
