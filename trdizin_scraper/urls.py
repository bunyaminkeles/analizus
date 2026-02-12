from django.urls import path
from . import views

app_name = 'trdizin_scraper'

urlpatterns = [
    path('', views.search_page, name='search'),
]
