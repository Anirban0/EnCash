"""
Bank SMS transaction-alert parser.

Extracts amount, direction, account last-4, merchant, date and (optional)
balance from the short, semi-structured alerts that banks send, e.g.::

    Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON. Avl Bal Rs.5,000.00
    INR 500 credited to A/c no. XX5678 on 01-06-2026. Avl Bal INR 10,000
    Rs 250.00 spent on Card xx9999 at SWIGGY on 10-06-26

Input is a block of text with one alert per line. Non-transactional messages
(OTPs, promotions) are ignored; lines that look like transactions but cannot be
fully parsed are returned in ``unparsed`` for the user to review.
"""
from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .base import BaseParser, ParsedTxn, ParseResult

# A monetary amount, optionally prefixed by a currency marker.
_CURRENCY = r"(?:rs\.?|inr|₹)"
_AMOUNT = r"[\d,]+(?:\.\d{1,2})?"

_AMOUNT_RE = re.compile(rf"{_CURRENCY}\s*({_AMOUNT})", re.IGNORECASE)
_BALANCE_RE = re.compile(
    rf"(?:avl\.?\s*bal(?:ance)?|available\s*balance|bal(?:ance)?)\s*[:\-]?\s*"
    rf"{_CURRENCY}\s*({_AMOUNT})",
    re.IGNORECASE,
)
_ACCOUNT_RE = re.compile(
    r"(?:a/?c|acct|account|card)\s*(?:no\.?|number|ending)?\s*[:\-]?\s*"
    r"[xX*]*(\d{3,4})",
    re.IGNORECASE,
)
_MERCHANT_RES = [
    re.compile(r"\b(?:VPA|UPI)[:/ ]+([A-Za-z0-9.\-@_]+)", re.IGNORECASE),
    re.compile(
        r"\b(?:at|to|towards|favouring|info[:\-]?)\s+"
        r"([A-Za-z0-9&._\-*@ ]+?)"
        r"(?:\s+on\b|\.\s|\.$|,|\s+avl\b|\s+bal\b|\s+ref\b|$)",
        re.IGNORECASE,
    ),
]
_DATE_RE = re.compile(
    r"\b(\d{1,2}[-/ ](?:[A-Za-z]{3,9}|\d{1,2})[-/ ]\d{2,4})\b"
)

_DEBIT_KEYWORDS = (
    "debited", "debit", "spent", "withdrawn", "withdraw", "paid",
    "purchase", "deducted", "sent", "transferred", "txn of",
)
_CREDIT_KEYWORDS = (
    "credited", "credit", "received", "deposited", "refund", "added",
)
# Lines matching these are noise, never transactions.
_IGNORE_RE = re.compile(
    r"\b(otp|one[\s-]?time[\s-]?password|verification code|do not share|"
    r"e-?statement|will be|reminder|due on|offer|cashback|congratulations|"
    r"download|click)\b",
    re.IGNORECASE,
)

_DATE_FORMATS = (
    "%d-%b-%y", "%d-%b-%Y", "%d %b %y", "%d %b %Y",
    "%d/%b/%y", "%d/%b/%Y",
    "%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y", "%d %m %Y",
)


def _to_decimal(raw: str) -> Decimal | None:
    try:
        return Decimal(raw.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None


def _parse_date(token: str):
    token = token.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            continue
    return None


def _detect_direction(text: str) -> str | None:
    lowered = text.lower()
    # Check debit and credit keyword positions; earliest wins to handle
    # messages that mention both (e.g. a debit that quotes the balance).
    debit_pos = min(
        (lowered.find(k) for k in _DEBIT_KEYWORDS if k in lowered), default=-1
    )
    credit_pos = min(
        (lowered.find(k) for k in _CREDIT_KEYWORDS if k in lowered), default=-1
    )
    if debit_pos == -1 and credit_pos == -1:
        return None
    if credit_pos == -1:
        return "debit"
    if debit_pos == -1:
        return "credit"
    return "debit" if debit_pos < credit_pos else "credit"


def _extract_amount(text: str, balance_span) -> Decimal | None:
    """First currency amount that is not the balance amount."""
    for match in _AMOUNT_RE.finditer(text):
        if balance_span and balance_span[0] <= match.start() < balance_span[1]:
            continue
        amount = _to_decimal(match.group(1))
        if amount is not None:
            return amount
    return None


def _extract_merchant(text: str) -> str:
    for pattern in _MERCHANT_RES:
        match = pattern.search(text)
        if match:
            merchant = match.group(1).strip(" .,-")
            # Drop a trailing standalone "on" left by greedy matching.
            merchant = re.sub(r"\s+on$", "", merchant, flags=re.IGNORECASE).strip()
            if merchant:
                return merchant[:128]
    return ""


class SmsParser(BaseParser):
    source = "sms"

    def parse(self, raw: str) -> ParseResult:
        result = ParseResult()
        for line in raw.splitlines():
            message = line.strip()
            if not message:
                continue
            parsed = self._parse_message(message)
            if parsed is not None:
                result.transactions.append(parsed)
            elif self._looks_transactional(message):
                result.unparsed.append(message)
            # otherwise: non-transactional noise, ignored silently.
        return result

    @staticmethod
    def _looks_transactional(message: str) -> bool:
        return bool(_AMOUNT_RE.search(message)) and not _IGNORE_RE.search(message)

    def _parse_message(self, message: str) -> ParsedTxn | None:
        if _IGNORE_RE.search(message):
            return None

        direction = _detect_direction(message)
        if direction is None:
            return None

        balance_match = _BALANCE_RE.search(message)
        balance_span = balance_match.span() if balance_match else None
        amount = _extract_amount(message, balance_span)
        if amount is None:
            return None

        date_match = _DATE_RE.search(message)
        txn_date = _parse_date(date_match.group(1)) if date_match else None
        if txn_date is None:
            return None

        account_match = _ACCOUNT_RE.search(message)
        balance_after = (
            _to_decimal(balance_match.group(1)) if balance_match else None
        )

        return ParsedTxn(
            date=txn_date,
            amount=amount,
            direction=direction,
            description=message,
            merchant=_extract_merchant(message),
            account_last4=(account_match.group(1)[-4:] if account_match else ""),
            balance_after=balance_after,
            currency="INR",
            raw_text=message,
        )
