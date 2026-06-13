"""Test settings: dev config with rate-throttling disabled.

Throttling is exercised by a dedicated test (see tests/test_api.py); leaving it
on globally would make unrelated tests flaky as they share the cache.
"""
from .dev import *  # noqa: F401,F403
from .dev import REST_FRAMEWORK

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": (),
    "DEFAULT_THROTTLE_RATES": {},
}
