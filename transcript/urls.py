from django.urls import path
from . import views

app_name = "transcript"

urlpatterns = [
    path("", views.transcript_form, name="form"),
    path("status/<int:job_id>/", views.transcript_status, name="status"),
    path("status/<int:job_id>/api/", views.transcript_status_api, name="status_api"),
    path("download/<int:job_id>/", views.transcript_download, name="download"),
]
