"""
Development settings.

Uses SQLite by default so the project runs (and tests pass) without a separate
database server. Set ``USE_POSTGRES=1`` (and the POSTGRES_* vars) to use the
PostgreSQL config from base.py instead.
"""
import os

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env_bool

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

if not env_bool("USE_POSTGRES", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Allow the Vite dev server during local development.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
