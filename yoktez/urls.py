from django.urls import path
from . import views

app_name = 'yoktez'

urlpatterns = [
    path('', views.yoktez_landing, name='landing'),
    path('status/<uuid:job_id>/', views.yoktez_job_status, name='job_status'),
    path('download/<uuid:job_id>/', views.yoktez_download, name='download'),
    path('send-demo/<uuid:job_id>/', views.yoktez_send_demo_email, name='send_demo'),
]
