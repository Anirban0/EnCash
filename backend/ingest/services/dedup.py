"""Stable fingerprinting so the same alert is never imported twice."""
from __future__ import annotations

import hashlib
from datetime import date
from decimal import Decimal


def dedup_hash(
    *,
    txn_date: date,
    amount: Decimal,
    direction: str,
    account_last4: str,
) -> str:
    """A deterministic fingerprint for a transaction.

    Based on the fields that identify a real-world transaction regardless of
    surrounding text, so re-pasting the same SMS produces the same hash.
    """
    normalized = "|".join(
        [
            txn_date.isoformat(),
            f"{Decimal(amount):.2f}",
            direction,
            (account_last4 or "").strip(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
