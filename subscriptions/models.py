from django.conf import settings
from django.db import models

from orders.models import Order
from product.models import AISubscriptionPlan


class UserAISubscription(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    class DeliveryStatus(models.TextChoices):
        WAITING_FOR_PAYMENT = "waiting_for_payment", "Waiting For Payment"
        WAITING_FOR_ADMIN = "waiting_for_admin", "Waiting For Admin"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_subscriptions",
    )
    plan = models.ForeignKey(
        AISubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="user_subscriptions",
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="ai_subscription",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    delivery_status = models.CharField(
        max_length=30,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.WAITING_FOR_ADMIN,
    )
    activation_gmail = models.EmailField(blank=True)
    delivery_note = models.TextField(blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"
