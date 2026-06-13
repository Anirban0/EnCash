import pytest

from transactions.models import Transaction

from .conftest import SAMPLE_SMS

pytestmark = pytest.mark.django_db


# --- Auth -------------------------------------------------------------------
def test_register_and_login_flow(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {"email": "new@example.com", "password": "Str0ngPass!99"},
        format="json",
    )
    assert resp.status_code == 201

    resp = api_client.post(
        "/api/auth/token/",
        {"email": "new@example.com", "password": "Str0ngPass!99"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data


def test_weak_password_rejected(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {"email": "weak@example.com", "password": "123"},
        format="json",
    )
    assert resp.status_code == 400


def test_protected_route_requires_auth(api_client):
    assert api_client.get("/api/transactions/").status_code == 401
    assert api_client.get("/api/analytics/summary/").status_code == 401


def test_logout_blacklists_refresh_token(api_client, user):
    tok = api_client.post(
        "/api/auth/token/",
        {"email": "alice@example.com", "password": "Sup3rSecret!1"},
        format="json",
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok['access']}")
    logout = api_client.post("/api/auth/logout/", {"refresh": tok["refresh"]}, format="json")
    assert logout.status_code == 205
    # The blacklisted refresh token can no longer be used.
    refresh = api_client.post(
        "/api/auth/token/refresh/", {"refresh": tok["refresh"]}, format="json"
    )
    assert refresh.status_code == 401


# --- Ingest pipeline --------------------------------------------------------
def test_ingest_creates_transactions(auth_client):
    resp = auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    assert resp.status_code == 200
    assert resp.data["inserted"] == 4
    assert resp.data["duplicates"] == 0
    assert resp.data["unparsed"] == []


def test_reingest_is_deduplicated(auth_client):
    auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    resp = auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    assert resp.data["inserted"] == 0
    assert resp.data["duplicates"] == 4


def test_ingested_transactions_are_categorized(auth_client):
    auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    amazon = Transaction.objects.get(merchant__icontains="amazon")
    assert amazon.category is not None
    assert amazon.category.name == "Shopping"


# --- Per-user isolation -----------------------------------------------------
def test_users_cannot_see_each_others_transactions(api_client, user, other_user):
    # Alice ingests.
    tok = api_client.post(
        "/api/auth/token/",
        {"email": "alice@example.com", "password": "Sup3rSecret!1"},
        format="json",
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok['access']}")
    api_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")

    # Bob sees nothing.
    tok2 = api_client.post(
        "/api/auth/token/",
        {"email": "bob@example.com", "password": "Sup3rSecret!2"},
        format="json",
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok2['access']}")
    resp = api_client.get("/api/transactions/")
    assert resp.data["count"] == 0


def test_user_cannot_access_other_users_transaction_by_id(api_client, user, other_user):
    tok = api_client.post(
        "/api/auth/token/",
        {"email": "alice@example.com", "password": "Sup3rSecret!1"},
        format="json",
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok['access']}")
    api_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    alice_txn_id = Transaction.objects.first().id

    tok2 = api_client.post(
        "/api/auth/token/",
        {"email": "bob@example.com", "password": "Sup3rSecret!2"},
        format="json",
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok2['access']}")
    assert api_client.get(f"/api/transactions/{alice_txn_id}/").status_code == 404


# --- Analytics --------------------------------------------------------------
def test_analytics_summary(auth_client):
    auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    resp = auth_client.get("/api/analytics/summary/")
    assert resp.status_code == 200
    # 500 credited; 1200 + 250 + 2000 = 3450 debited.
    assert resp.data["income"] == "500.00"
    assert resp.data["expense"] == "3450.00"
    assert resp.data["net"] == "-2950.00"
    assert resp.data["count"] == 4


def test_analytics_by_category_and_trend(auth_client):
    auth_client.post("/api/ingest/sms/", {"raw": SAMPLE_SMS}, format="json")
    by_cat = auth_client.get("/api/analytics/by-category/")
    assert by_cat.status_code == 200
    assert any(row["category"] == "Shopping" for row in by_cat.data)

    trend = auth_client.get("/api/analytics/trend/")
    assert trend.status_code == 200
    assert len(trend.data) >= 1
