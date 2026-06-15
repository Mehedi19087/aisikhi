from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import AISubscriptionPlan, Product


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(
        max_length=80,
        validators=[UniqueValidator(queryset=Product.objects.all())],
    )
    description = serializers.CharField(required=False, allow_blank=True)


class ProductUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=80)
    description = serializers.CharField(required=False, allow_blank=True)


class ProductResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AISubscriptionPlanCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    account_type = serializers.ChoiceField(choices=AISubscriptionPlan.AccountType.choices)
    duration_days = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    title = serializers.CharField(max_length=200)
    features = serializers.CharField(required=False, allow_blank=True)
    rules = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class AISubscriptionPlanUpdateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    account_type = serializers.ChoiceField(choices=AISubscriptionPlan.AccountType.choices)
    duration_days = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    title = serializers.CharField(max_length=200)
    features = serializers.CharField(required=False, allow_blank=True)
    rules = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class AISubscriptionPlanResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = ProductResponseSerializer(read_only=True)
    account_type = serializers.CharField(read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    title = serializers.CharField(read_only=True)
    features = serializers.CharField(read_only=True)
    rules = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
