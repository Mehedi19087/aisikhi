from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from .models import UserAISubscription


def get_user_ai_subscriptions(user_id):
    try:
        return UserAISubscription.objects.select_related(
            "plan",
            "plan__product",
            "order",
            "order__ai_subscription_plan",
            "order__ai_subscription_plan__product",
        ).filter(user_id=user_id).order_by("-created_at")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_user_ai_subscription(id, user_id):
    try:
        return UserAISubscription.objects.select_related(
            "plan",
            "plan__product",
            "order",
            "order__ai_subscription_plan",
            "order__ai_subscription_plan__product",
        ).get(id=id, user_id=user_id)
    except ObjectDoesNotExist:
        raise LookupError("AI subscription not found")


def get_active_user_ai_subscription(user_id):
    try:
        now = timezone.now()
        return UserAISubscription.objects.select_related(
            "plan",
            "plan__product",
            "order",
            "order__ai_subscription_plan",
            "order__ai_subscription_plan__product",
        ).filter(
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
            user_id=user_id,
            status=UserAISubscription.Status.ACTIVE,
        ).order_by("-created_at").first()
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
