import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="alice@example.com", password="Sup3rSecret!1")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="bob@example.com", password="Sup3rSecret!2")


@pytest.fixture
def auth_client(api_client, user):
    resp = api_client.post(
        "/api/auth/token/",
        {"email": "alice@example.com", "password": "Sup3rSecret!1"},
        format="json",
    )
    token = resp.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


SAMPLE_SMS = """\
Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON. Avl Bal Rs.5,000.00
INR 500 credited to A/c no. XX5678 on 01-06-2026. Avl Bal INR 10,000
Rs 250.00 spent on Card xx9999 at SWIGGY on 10-06-26
Rs.2000 withdrawn from A/c XX1234 at ATM on 03-06-2026
Your OTP is 123456. Do not share it with anyone.
Get 10% cashback! Download our app now and click here.
"""
