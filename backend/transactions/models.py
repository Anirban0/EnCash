from django.conf import settings
from django.db import models


class Direction(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class Source(models.TextChoices):
    SMS = "sms", "SMS alert"
    PDF = "pdf", "PDF statement"
    EXCEL = "excel", "Excel / CSV"


class Category(models.Model):
    """
    A spending/income category.

    ``user`` is null for the global, seeded default categories that every user
    sees; a non-null ``user`` marks a category owned by a single user.
    """

    name = models.CharField(max_length=64)
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Merchant/description keywords that map to this category.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="uniq_category_per_user"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    """A single normalized ledger entry, owned by one user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    direction = models.CharField(max_length=6, choices=Direction.choices)
    description = models.CharField(max_length=255, blank=True)
    merchant = models.CharField(max_length=128, blank=True)
    account_last4 = models.CharField(max_length=4, blank=True)
    balance_after = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
    )
    source = models.CharField(max_length=8, choices=Source.choices, default=Source.SMS)
    raw_text = models.TextField(blank=True)
    # Stable fingerprint used to detect re-imports of the same alert.
    dedup_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "dedup_hash"], name="uniq_txn_per_user"
            )
        ]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "direction"]),
        ]

    def __str__(self) -> str:
        return f"{self.date} {self.direction} {self.amount} {self.merchant}".strip()
