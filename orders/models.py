from django.conf import settings
from django.db import models

from product.models import AISubscriptionPlan


class Order(models.Model):
    class OrderType(models.TextChoices):
        AI_SUBSCRIPTION = "ai_subscription", "AI Subscription"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentMethod(models.TextChoices):
        BKASH = "bkash", "Bkash"
        NAGAD = "nagad", "Nagad"
        ROCKET = "rocket", "Rocket"
        BANK = "bank", "Bank"
        MANUAL = "manual", "Manual"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    order_type = models.CharField(
        max_length=30,
        choices=OrderType.choices,
        default=OrderType.AI_SUBSCRIPTION,
    )
    ai_subscription_plan = models.ForeignKey(
        AISubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    transaction_id = models.CharField(max_length=120)
    payment_screenshot = models.FileField(
        upload_to="payment_screenshots/",
        blank=True,
        null=True,
    )
    activation_gmail = models.EmailField(blank=True)
    customer_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"
