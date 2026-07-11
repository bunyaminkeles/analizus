from django.urls import path
from . import views

urlpatterns = [
    path('', views.analiz_hub, name='analiz_home'),
    path('clear-session/', views.clear_session_dataset, name='analiz_clear_session'),
    path('hero-upload/', views.hero_upload, name='hero_upload'),
    path('<slug:tool_slug>/', views.analiz_console, name='analiz_console'),
]
