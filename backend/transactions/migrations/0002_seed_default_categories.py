"""Seed the global default categories (user=None) every user can use."""
from django.db import migrations

DEFAULT_CATEGORIES = [
    ("Food", ["swiggy", "zomato", "restaurant", "cafe", "dominos", "mcdonald",
              "starbucks", "food", "bakery", "dineout"]),
    ("Transport", ["uber", "ola", "rapido", "irctc", "petrol", "fuel", "metro",
                   "fastag", "indianoil", "hp ", "bharat petroleum", "redbus"]),
    ("Shopping", ["amazon", "flipkart", "myntra", "ajio", "nykaa", "mall",
                  "store", "retail", "shop", "meesho"]),
    ("Bills", ["electricity", "recharge", "airtel", "jio", "vodafone", "bill",
               "broadband", "gas", "water", "dth", "insurance", "lic"]),
    ("Entertainment", ["netflix", "spotify", "hotstar", "prime", "bookmyshow",
                       "pvr", "inox", "youtube", "gaming"]),
    ("Income", ["salary", "credited", "interest", "dividend", "refund",
                "cashback", "neft", "imps cr"]),
    ("Transfers", ["upi", "transfer", "neft", "imps", "rtgs", "sent to"]),
    ("ATM", ["atm", "cash withdrawal", "withdrawn"]),
    ("Other", []),
]


def seed(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    for name, keywords in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name, user=None, defaults={"keywords": keywords}
        )


def unseed(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    Category.objects.filter(
        user=None, name__in=[c[0] for c in DEFAULT_CATEGORIES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("transactions", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
