from django.urls import path
from . import views

app_name = 'yoktez'

urlpatterns = [
    path('', views.yoktez_landing, name='landing'),
    path('status/<uuid:job_id>/', views.yoktez_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.yoktez_send_demo_email, name='send_demo'),
    path('siparis/<uuid:job_id>/', views.yoktez_order_page, name='order'),
    path('debug-email-test-8c4b2a9f1e/', views.debug_email_test, name='debug_email_test'),
]
