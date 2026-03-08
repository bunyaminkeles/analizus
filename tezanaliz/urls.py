from django.urls import path
from . import views

app_name = 'tezanaliz'

urlpatterns = [
    path('', views.tezanaliz_landing, name='landing'),
    path('yok/<uuid:yok_job_id>/', views.create_from_yoktez, name='from_yoktez'),
    path('status/<uuid:job_id>/', views.tezanaliz_status, name='status'),
    path('sonuc/<uuid:job_id>/', views.tezanaliz_results, name='results'),
]
