"""
Rule-based categorization.

Matches a transaction's merchant/description against the keyword lists attached
to each available category (the global defaults plus the user's own). Credits
default to "Income" and anything unmatched falls back to "Other". This is a
deliberately simple, transparent first pass; ML/LLM categorization is a planned
follow-up that can slot in behind the same interface.
"""
from __future__ import annotations

from django.db.models import Q

from transactions.models import Category

from ..parsers.base import ParsedTxn


class Categorizer:
    """Resolves a :class:`ParsedTxn` to a :class:`Category` for one user."""

    def __init__(self, user):
        # Cache the user's visible categories once per ingest batch.
        self._categories = list(
            Category.objects.filter(Q(user__isnull=True) | Q(user=user))
        )
        self._by_name = {c.name.lower(): c for c in self._categories}

    def categorize(self, txn: ParsedTxn) -> Category | None:
        haystack = f"{txn.merchant} {txn.description}".lower()
        for category in self._categories:
            for keyword in category.keywords or []:
                if keyword.lower() in haystack:
                    return category
        if txn.direction == "credit":
            return self._by_name.get("income")
        return self._by_name.get("other")
