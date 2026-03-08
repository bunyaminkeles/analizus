from django.urls import path
from . import views

app_name = 'makaleanaliz'

urlpatterns = [
    path('dizin/<uuid:dizin_job_id>/', views.create_from_dizin, name='from_dizin'),
    path('status/<uuid:job_id>/', views.makaleanaliz_status, name='status'),
    path('sonuc/<uuid:job_id>/', views.makaleanaliz_results, name='results'),
]
