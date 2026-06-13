from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "direction", "amount", "merchant", "category", "user")
    list_filter = ("direction", "source")
    search_fields = ("merchant", "description")
    raw_id_fields = ("user", "category")
