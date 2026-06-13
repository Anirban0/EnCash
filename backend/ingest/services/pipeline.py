"""
Ingest pipeline orchestration.

parse -> normalize -> categorize -> dedup -> store, all scoped to one user.
The parser is injected, so the same pipeline serves SMS today and PDF/Excel
later without modification.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from django.db import transaction as db_transaction

from transactions.models import Transaction

from ..parsers.base import BaseParser
from .categorizer import Categorizer
from .dedup import dedup_hash

audit = logging.getLogger("encash.audit")


@dataclass
class IngestSummary:
    inserted: int = 0
    duplicates: int = 0
    unparsed: list[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.unparsed is None:
            self.unparsed = []


def run_ingest(*, user, raw: str, parser: BaseParser) -> IngestSummary:
    """Parse ``raw`` with ``parser`` and persist new transactions for ``user``."""
    result = parser.parse(raw)
    summary = IngestSummary(unparsed=list(result.unparsed))

    if not result.transactions:
        return summary

    categorizer = Categorizer(user)

    # Dedup within the batch first, then against what is already stored.
    seen_hashes: set[str] = set()
    existing_hashes = set(
        Transaction.objects.filter(user=user).values_list("dedup_hash", flat=True)
    )

    to_create: list[Transaction] = []
    for parsed in result.transactions:
        fingerprint = dedup_hash(
            txn_date=parsed.date,
            amount=parsed.amount,
            direction=parsed.direction,
            account_last4=parsed.account_last4,
        )
        if fingerprint in existing_hashes or fingerprint in seen_hashes:
            summary.duplicates += 1
            continue
        seen_hashes.add(fingerprint)
        to_create.append(
            Transaction(
                user=user,
                date=parsed.date,
                amount=parsed.amount,
                currency=parsed.currency,
                direction=parsed.direction,
                description=parsed.description[:255],
                merchant=parsed.merchant,
                account_last4=parsed.account_last4,
                balance_after=parsed.balance_after,
                category=categorizer.categorize(parsed),
                source=parser.source,
                raw_text=parsed.raw_text,
                dedup_hash=fingerprint,
            )
        )

    if to_create:
        with db_transaction.atomic():
            # ignore_conflicts guards against a race on the unique constraint.
            Transaction.objects.bulk_create(to_create, ignore_conflicts=True)
        summary.inserted = len(to_create)

    # Audit without logging any monetary values or merchant names.
    audit.info(
        "ingest source=%s user=%s inserted=%s duplicates=%s unparsed=%s",
        parser.source,
        user.id,
        summary.inserted,
        summary.duplicates,
        len(summary.unparsed),
    )
    return summary
