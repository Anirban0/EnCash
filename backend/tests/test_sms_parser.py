from datetime import date
from decimal import Decimal

from ingest.parsers.sms_parser import SmsParser

from .conftest import SAMPLE_SMS


def parse(text):
    return SmsParser().parse(text)


def test_parses_debit_with_balance_and_merchant():
    result = parse(
        "Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON. "
        "Avl Bal Rs.5,000.00"
    )
    assert len(result.transactions) == 1
    txn = result.transactions[0]
    assert txn.direction == "debit"
    assert txn.amount == Decimal("1200.00")
    assert txn.balance_after == Decimal("5000.00")
    assert txn.date == date(2026, 6, 12)
    assert txn.account_last4 == "1234"
    assert "AMAZON" in txn.merchant.upper()


def test_parses_credit():
    result = parse(
        "INR 500 credited to A/c no. XX5678 on 01-06-2026. Avl Bal INR 10,000"
    )
    txn = result.transactions[0]
    assert txn.direction == "credit"
    assert txn.amount == Decimal("500")
    assert txn.account_last4 == "5678"
    assert txn.date == date(2026, 6, 1)


def test_parses_card_spend():
    result = parse("Rs 250.00 spent on Card xx9999 at SWIGGY on 10-06-26")
    txn = result.transactions[0]
    assert txn.direction == "debit"
    assert txn.amount == Decimal("250.00")
    assert "SWIGGY" in txn.merchant.upper()


def test_atm_withdrawal_is_debit():
    result = parse("Rs.2000 withdrawn from A/c XX1234 at ATM on 03-06-2026")
    txn = result.transactions[0]
    assert txn.direction == "debit"
    assert txn.amount == Decimal("2000")


def test_otp_and_promo_are_ignored_not_unparsed():
    result = parse(
        "Your OTP is 123456. Do not share it with anyone.\n"
        "Get 10% cashback! Download our app now and click here."
    )
    assert result.transactions == []
    assert result.unparsed == []


def test_amount_is_not_confused_with_balance():
    result = parse(
        "Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON. "
        "Avl Bal Rs.5,000.00"
    )
    txn = result.transactions[0]
    # The transaction amount must be 1200, never the 5000 balance.
    assert txn.amount == Decimal("1200.00")


def test_sample_batch_counts():
    result = parse(SAMPLE_SMS)
    assert len(result.transactions) == 4
    assert result.unparsed == []
    directions = sorted(t.direction for t in result.transactions)
    assert directions == ["credit", "debit", "debit", "debit"]


def test_transactional_but_unparseable_line_is_reported():
    # Has an amount + direction but no recognizable date -> unparsed.
    result = parse("Rs.999 debited from A/c XX1234 at SOMEPLACE")
    assert result.transactions == []
    assert len(result.unparsed) == 1
