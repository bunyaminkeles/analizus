from django.urls import path
from . import views

app_name = 'oaipmh'

urlpatterns = [
    path('', views.oaipmh_landing, name='landing'),
    path('status/<uuid:job_id>/', views.oaipmh_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.oaipmh_send_demo_email, name='send_demo_email'),
    path('cancel/<uuid:job_id>/', views.oaipmh_cancel, name='cancel'),
    path('siparis/<uuid:job_id>/', views.oaipmh_order_page, name='order_page'),
]
