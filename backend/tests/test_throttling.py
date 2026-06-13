"""Verify that the throttling mechanism actually rejects bursts.

DRF binds ``throttle_classes`` at import time, so ``override_settings`` cannot
change a view's throttle after the fact. We instead attach an explicit
low-rate throttle to the auth view for the duration of the test, which
exercises the same code path that protects the real endpoints in production.
"""
import pytest
from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle

from accounts.views import RegisterView

pytestmark = pytest.mark.django_db


class BurstThrottle(SimpleRateThrottle):
    scope = "burst"

    def get_rate(self):
        return "2/min"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


def test_auth_endpoint_is_throttled(api_client, monkeypatch):
    monkeypatch.setattr(RegisterView, "throttle_classes", [BurstThrottle])
    payload = {"password": "Str0ngPass!99"}

    r1 = api_client.post("/api/auth/register/", {**payload, "email": "a@x.com"}, format="json")
    r2 = api_client.post("/api/auth/register/", {**payload, "email": "b@x.com"}, format="json")
    r3 = api_client.post("/api/auth/register/", {**payload, "email": "c@x.com"}, format="json")

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 429  # third request in the window is throttled


def test_real_endpoints_declare_throttle_scopes():
    from ingest.views import SmsIngestView

    assert RegisterView.throttle_scope == "auth"
    assert SmsIngestView.throttle_scope == "ingest"
