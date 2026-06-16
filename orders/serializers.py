from rest_framework import serializers

from product.models import AISubscriptionPlan
from product.serializers import AISubscriptionPlanResponseSerializer

from .models import Order


class CreateAISubscriptionOrderSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=AISubscriptionPlan.objects.all())
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    transaction_id = serializers.CharField(max_length=120)
    payment_screenshot = serializers.FileField(required=False, allow_empty_file=False)
    activation_gmail = serializers.EmailField(required=False, allow_blank=True)
    customer_note = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices, required=False)
    transaction_id = serializers.CharField(max_length=120, required=False)
    payment_screenshot = serializers.FileField(required=False, allow_empty_file=False)
    activation_gmail = serializers.EmailField(required=False, allow_blank=True)
    customer_note = serializers.CharField(required=False, allow_blank=True)


class AdminUpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(
            (Order.Status.APPROVED, "Approved"),
            (Order.Status.REJECTED, "Rejected"),
        )
    )
    admin_note = serializers.CharField(required=False, allow_blank=True)


class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order_type = serializers.CharField(read_only=True)
    ai_subscription_plan = AISubscriptionPlanResponseSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    payment_screenshot = serializers.FileField(read_only=True)
    activation_gmail = serializers.EmailField(read_only=True)
    customer_note = serializers.CharField(read_only=True)
    admin_note = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
