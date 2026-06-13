from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TransactionViewSet

router = DefaultRouter()
router.register("transactions", TransactionViewSet, basename="transaction")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
