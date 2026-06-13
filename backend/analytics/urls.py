from django.urls import path

from .views import ByCategoryView, SummaryView, TopMerchantsView, TrendView

urlpatterns = [
    path("summary/", SummaryView.as_view(), name="analytics_summary"),
    path("by-category/", ByCategoryView.as_view(), name="analytics_by_category"),
    path("trend/", TrendView.as_view(), name="analytics_trend"),
    path("top-merchants/", TopMerchantsView.as_view(), name="analytics_top_merchants"),
]
