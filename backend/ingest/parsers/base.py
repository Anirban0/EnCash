"""
Parser interface shared by every data source.

Each source (SMS now; PDF and Excel later) implements :class:`BaseParser` and
returns a list of :class:`ParsedTxn` value objects plus any raw fragments that
could not be parsed. Keeping every parser behind this single contract means the
ingest pipeline, normalization, categorization and dedup logic never need to
know which source the data came from.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class ParsedTxn:
    """A source-agnostic transaction extracted from raw input."""

    date: date
    amount: Decimal
    direction: str  # "debit" | "credit" (see transactions.models.Direction)
    description: str = ""
    merchant: str = ""
    account_last4: str = ""
    balance_after: Decimal | None = None
    currency: str = "INR"
    raw_text: str = ""


@dataclass
class ParseResult:
    transactions: list[ParsedTxn] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)


class BaseParser(abc.ABC):
    """Common contract for all source parsers."""

    #: matches ``transactions.models.Source`` values.
    source: str

    @abc.abstractmethod
    def parse(self, raw: str) -> ParseResult:
        """Parse raw input into transactions plus any unparsed fragments."""
        raise NotImplementedError
