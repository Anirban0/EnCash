from rest_framework import serializers

from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "keywords")


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "date",
            "amount",
            "currency",
            "direction",
            "description",
            "merchant",
            "account_last4",
            "balance_after",
            "category",
            "category_name",
            "source",
            "created_at",
        )
        # The ledger is built by the ingest pipeline; via the API a user may
        # only re-assign the category of an existing transaction.
        read_only_fields = (
            "id",
            "date",
            "amount",
            "currency",
            "direction",
            "description",
            "merchant",
            "account_last4",
            "balance_after",
            "source",
            "created_at",
        )

    def validate_category(self, category):
        if category is None:
            return category
        user = self.context["request"].user
        # Only global defaults or the user's own categories are assignable.
        if category.user_id not in (None, user.id):
            raise serializers.ValidationError("Invalid category.")
        return category
