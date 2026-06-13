from django.urls import path

from .views import SmsIngestView

urlpatterns = [
    path("sms/", SmsIngestView.as_view(), name="ingest_sms"),
]
