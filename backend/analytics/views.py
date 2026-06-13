"""
Read-only analytics aggregations for the dashboard.

Every query is filtered to ``request.user`` and supports optional
``date_from`` / ``date_to`` (inclusive, ``YYYY-MM-DD``) query parameters.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction


def _decimal(value) -> str:
    value = value if value is not None else Decimal("0")
    return str(Decimal(value).quantize(Decimal("0.01")))


class _AnalyticsView(APIView):
    """Shared per-user, date-bounded queryset for analytics endpoints."""

    def get_queryset(self, request):
        qs = Transaction.objects.filter(user=request.user)
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from and (parsed := self._parse(date_from)):
            qs = qs.filter(date__gte=parsed)
        if date_to and (parsed := self._parse(date_to)):
            qs = qs.filter(date__lte=parsed)
        return qs

    @staticmethod
    def _parse(value: str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None


class SummaryView(_AnalyticsView):
    """Total income, expense, net and transaction count for the period."""

    def get(self, request):
        qs = self.get_queryset(request)
        income = qs.filter(direction="credit").aggregate(s=Sum("amount"))["s"]
        expense = qs.filter(direction="debit").aggregate(s=Sum("amount"))["s"]
        income = income or Decimal("0")
        expense = expense or Decimal("0")
        return Response(
            {
                "income": _decimal(income),
                "expense": _decimal(expense),
                "net": _decimal(income - expense),
                "count": qs.count(),
            }
        )


class ByCategoryView(_AnalyticsView):
    """Expense totals grouped by category."""

    def get(self, request):
        rows = (
            self.get_queryset(request)
            .filter(direction="debit")
            .values("category__name")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        data = [
            {
                "category": row["category__name"] or "Uncategorized",
                "total": _decimal(row["total"]),
                "count": row["count"],
            }
            for row in rows
        ]
        return Response(data)


class TrendView(_AnalyticsView):
    """Monthly income vs. expense series."""

    def get(self, request):
        rows = (
            self.get_queryset(request)
            .annotate(month=TruncMonth("date"))
            .values("month", "direction")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        buckets: dict[str, dict[str, str]] = {}
        for row in rows:
            key = row["month"].strftime("%Y-%m")
            bucket = buckets.setdefault(
                key, {"month": key, "income": "0", "expense": "0"}
            )
            field = "income" if row["direction"] == "credit" else "expense"
            bucket[field] = _decimal(row["total"])
        return Response(list(buckets.values()))


class TopMerchantsView(_AnalyticsView):
    """Top expense merchants for the period."""

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 10)), 50)
        rows = (
            self.get_queryset(request)
            .filter(direction="debit")
            .exclude(merchant="")
            .values("merchant")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")[:limit]
        )
        data = [
            {
                "merchant": row["merchant"],
                "total": _decimal(row["total"]),
                "count": row["count"],
            }
            for row in rows
        ]
        return Response(data)
