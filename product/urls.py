from django.urls import path

from .views import (
    AISubscriptionPlanDetailsApiView,
    AISubscriptionPlanListCreateApiView,
    ProductDetailsApiView,
    ProductListCreateApiView,
)


urlpatterns = [
    path("products/", ProductListCreateApiView.as_view(), name="product-list-create"),
    path("products/<int:id>/", ProductDetailsApiView.as_view(), name="product-detail"),
    path(
        "ai-subscription-plans/",
        AISubscriptionPlanListCreateApiView.as_view(),
        name="ai-subscription-plan-list-create",
    ),
    path(
        "ai-subscription-plans/<int:id>/",
        AISubscriptionPlanDetailsApiView.as_view(),
        name="ai-subscription-plan-detail",
    ),
]
