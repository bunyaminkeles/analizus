from django.urls import path
from . import views

app_name = 'bibliometrics'

urlpatterns = [
    path('', views.bibliometrics_landing, name='landing'),
    path('status/<uuid:job_id>/', views.bibliometrics_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.bibliometrics_send_demo, name='send_demo'),
    path('siparis/<uuid:job_id>/', views.bibliometrics_order_page, name='order_page'),
    path('from-openalex/<uuid:alex_job_id>/', views.bibliometrics_from_openalex, name='from_openalex'),
]
