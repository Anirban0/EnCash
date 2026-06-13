from django.db.models import Q
from rest_framework import mixins, viewsets

from .filters import TransactionFilter
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """List/retrieve a user's transactions and re-categorize them.

    Creation happens through the ingest pipeline, and transactions are never
    deleted via this endpoint, so only safe + update verbs are exposed.
    """

    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    ordering_fields = ["date", "amount", "created_at"]

    def get_queryset(self):
        # Strict per-user isolation: a user can only ever see their own rows.
        return Transaction.objects.filter(user=self.request.user).select_related(
            "category"
        )


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Global default categories plus the requesting user's own categories."""

    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            Q(user__isnull=True) | Q(user=self.request.user)
        ).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
