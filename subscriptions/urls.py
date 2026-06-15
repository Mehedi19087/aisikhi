from django.urls import path

from .views import (
    MyActiveAISubscriptionApiView,
    MyAISubscriptionDetailsApiView,
    MyAISubscriptionListApiView,
)


urlpatterns = [
    path(
        "my/ai-subscriptions/",
        MyAISubscriptionListApiView.as_view(),
        name="my-ai-subscription-list",
    ),
    path(
        "my/ai-subscriptions/active/",
        MyActiveAISubscriptionApiView.as_view(),
        name="my-active-ai-subscription",
    ),
    path(
        "my/ai-subscriptions/<int:id>/",
        MyAISubscriptionDetailsApiView.as_view(),
        name="my-ai-subscription-detail",
    ),
]
