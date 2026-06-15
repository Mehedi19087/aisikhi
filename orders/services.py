from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import Order


def create_ai_subscription_order(user_id, validated_data):
    try:
        plan = validated_data.pop("plan")
        return Order.objects.create(
            user_id=user_id,
            order_type=Order.OrderType.AI_SUBSCRIPTION,
            ai_subscription_plan=plan,
            amount=plan.price,
            **validated_data,
        )
    except IntegrityError as e:
        raise ValueError(f"Database error while creating order: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_user_orders(user_id):
    try:
        return Order.objects.select_related(
            "ai_subscription_plan",
            "ai_subscription_plan__product",
        ).filter(user_id=user_id).order_by("-created_at")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_user_order(id, user_id):
    try:
        return Order.objects.select_related(
            "ai_subscription_plan",
            "ai_subscription_plan__product",
        ).get(id=id, user_id=user_id)
    except ObjectDoesNotExist:
        raise LookupError("order not found")


def update_user_order(id, user_id, data):
    try:
        order = Order.objects.get(id=id, user_id=user_id)
        if order.status != Order.Status.PENDING:
            raise ValueError("only pending orders can be updated")

        for key, value in data.items():
            setattr(order, key, value)
        order.save()
        return order
    except ObjectDoesNotExist:
        raise LookupError("order does not exist")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating order: {str(e)}")
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def cancel_user_order(id, user_id):
    try:
        order = Order.objects.get(id=id, user_id=user_id)
        if order.status != Order.Status.PENDING:
            raise ValueError("only pending orders can be cancelled")

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
    except ObjectDoesNotExist:
        raise LookupError("order does not exist")
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
