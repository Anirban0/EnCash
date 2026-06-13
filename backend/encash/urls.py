"""Root URL configuration for EnCash."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "encash"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", healthcheck, name="health"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("transactions.urls")),
    path("api/ingest/", include("ingest.urls")),
    path("api/analytics/", include("analytics.urls")),
]
