from django.urls import path
from . import views

app_name = 'trdizin'

urlpatterns = [
    path('', views.trdizin_landing, name='landing'),
    path('status/<uuid:job_id>/', views.trdizin_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.trdizin_send_demo_email, name='send_demo_email'),
    path('download/<uuid:job_id>/', views.trdizin_download, name='download'),
    path('download-excel/<uuid:job_id>/', views.trdizin_download_excel, name='download_excel'),
    path('cancel/<uuid:job_id>/', views.trdizin_cancel, name='cancel'),
    path('siparis/<uuid:job_id>/', views.trdizin_order_page, name='order_page'),
]
