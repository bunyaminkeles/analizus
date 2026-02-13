from django.urls import path
from . import views

app_name = 'trdizin'

urlpatterns = [
    path('', views.trdizin_landing, name='landing'),
    path('status/<uuid:job_id>/', views.trdizin_job_status, name='job_status'),
    path('send-demo/<uuid:job_id>/', views.trdizin_send_demo_email, name='send_demo_email'),
    path('siparis/<uuid:job_id>/', views.trdizin_order_page, name='order_page'),
]
