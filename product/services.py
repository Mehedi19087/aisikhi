from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .models import AISubscriptionPlan, Product


def create_product(validated_data):
    try:
        return Product.objects.create(**validated_data)
    except IntegrityError as e:
        raise ValueError(f"Database error while creating product: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_all_products():
    try:
        return Product.objects.all().order_by("-created_at")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_product(id):
    try:
        return Product.objects.get(id=id)
    except ObjectDoesNotExist:
        raise LookupError("product not found")


def update_product(id, data):
    try:
        product = Product.objects.get(id=id)
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        return product
    except ObjectDoesNotExist:
        raise LookupError("product does not exist")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating product: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def delete_product(id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
    except ObjectDoesNotExist:
        raise LookupError("product does not exist")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def create_ai_subscription_plan(validated_data):
    try:
        return AISubscriptionPlan.objects.create(**validated_data)
    except IntegrityError as e:
        raise ValueError(f"Database error while creating AI subscription plan: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_all_ai_subscription_plans():
    try:
        return AISubscriptionPlan.objects.select_related("product").order_by(
            "product__name",
            "account_type",
            "duration_days",
        )
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_ai_subscription_plan(id):
    try:
        return AISubscriptionPlan.objects.select_related("product").get(id=id)
    except ObjectDoesNotExist:
        raise LookupError("AI subscription plan not found")


def update_ai_subscription_plan(id, data):
    try:
        plan = AISubscriptionPlan.objects.get(id=id)
        for key, value in data.items():
            setattr(plan, key, value)
        plan.save()
        return plan
    except ObjectDoesNotExist:
        raise LookupError("AI subscription plan does not exist")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating AI subscription plan: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def delete_ai_subscription_plan(id):
    try:
        plan = AISubscriptionPlan.objects.get(id=id)
        plan.delete()
    except ObjectDoesNotExist:
        raise LookupError("AI subscription plan does not exist")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
