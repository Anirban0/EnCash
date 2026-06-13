"""
Production settings (cloud-hosted SaaS).

Enables the transport- and cookie-level hardening that is unnecessary (and
inconvenient) in local development. A real ``DJANGO_SECRET_KEY`` is mandatory.
"""
import os

from .base import *  # noqa: F401,F403
from .base import env_bool

DEBUG = False

if SECRET_KEY == "insecure-dev-key-change-me":  # noqa: F405
    raise RuntimeError(
        "DJANGO_SECRET_KEY must be set to a strong, unique value in production."
    )

# HTTPS / transport hardening (TLS terminates at the proxy in front of Django).
# Disable the redirect only when TLS is handled elsewhere or for local
# docker-compose testing over plain HTTP (DJANGO_SECURE_SSL_REDIRECT=0).
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Misc browser-protection headers.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
