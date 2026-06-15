from rest_framework import serializers

from orders.serializers import OrderResponseSerializer
from product.serializers import AISubscriptionPlanResponseSerializer


class UserAISubscriptionResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    plan = AISubscriptionPlanResponseSerializer(read_only=True)
    order = OrderResponseSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    delivery_status = serializers.CharField(read_only=True)
    activation_gmail = serializers.EmailField(read_only=True)
    delivery_note = serializers.CharField(read_only=True)
    starts_at = serializers.DateTimeField(read_only=True)
    ends_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
