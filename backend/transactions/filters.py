from django_filters import rest_framework as filters

from .models import Transaction


class TransactionFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["direction", "category", "source", "date_from", "date_to"]
