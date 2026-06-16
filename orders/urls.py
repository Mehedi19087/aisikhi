from django.urls import path

from .views import (
    AdminOrderDetailsApiView,
    CreateAISubscriptionOrderApiView,
    MyOrderDetailsApiView,
    MyOrderListApiView,
)


urlpatterns = [
    path(
        "orders/ai-subscription/",
        CreateAISubscriptionOrderApiView.as_view(),
        name="create-ai-subscription-order",
    ),
    path("my/orders/", MyOrderListApiView.as_view(), name="my-order-list"),
    path("my/orders/<int:id>/", MyOrderDetailsApiView.as_view(), name="my-order-detail"),
    path(
        "admin/orders/<int:id>/",
        AdminOrderDetailsApiView.as_view(),
        name="admin-order-detail",
    ),
]
