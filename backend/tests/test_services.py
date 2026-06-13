from datetime import date
from decimal import Decimal

import pytest

from ingest.parsers.base import ParsedTxn
from ingest.services.categorizer import Categorizer
from ingest.services.dedup import dedup_hash


def _txn(**kw):
    base = dict(
        date=date(2026, 6, 12),
        amount=Decimal("100"),
        direction="debit",
        account_last4="1234",
    )
    base.update(kw)
    return ParsedTxn(**base)


def test_dedup_hash_is_stable_and_distinct():
    a = dedup_hash(txn_date=date(2026, 6, 12), amount=Decimal("100.00"),
                   direction="debit", account_last4="1234")
    a_again = dedup_hash(txn_date=date(2026, 6, 12), amount=Decimal("100"),
                         direction="debit", account_last4="1234")
    different = dedup_hash(txn_date=date(2026, 6, 12), amount=Decimal("101"),
                           direction="debit", account_last4="1234")
    assert a == a_again  # 100 and 100.00 normalize identically
    assert a != different


@pytest.mark.django_db
def test_categorizer_matches_keyword(user):
    cat = Categorizer(user)
    txn = _txn(merchant="AMAZON", description="debited at AMAZON")
    category = cat.categorize(txn)
    assert category is not None
    assert category.name == "Shopping"


@pytest.mark.django_db
def test_categorizer_credit_defaults_to_income(user):
    cat = Categorizer(user)
    txn = _txn(direction="credit", merchant="", description="amount received")
    assert cat.categorize(txn).name == "Income"


@pytest.mark.django_db
def test_categorizer_unmatched_falls_back_to_other(user):
    cat = Categorizer(user)
    txn = _txn(merchant="ZZUNKNOWNZZ", description="debited somewhere")
    assert cat.categorize(txn).name == "Other"
