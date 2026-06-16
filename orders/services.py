from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.utils import timezone

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


def update_order_status_by_admin(id, data):
    from subscriptions.models import UserAISubscription

    try:
        with transaction.atomic():
            order = Order.objects.select_related("ai_subscription_plan").get(id=id)
            if order.status != Order.Status.PENDING:
                raise ValueError("only pending orders can be approved or rejected")

            new_status = data["status"]
            order.status = new_status
            order.admin_note = data.get("admin_note", order.admin_note)
            update_fields = ["status", "admin_note", "updated_at"]

            if new_status == Order.Status.APPROVED:
                now = timezone.now()
                order.approved_at = now
                update_fields.append("approved_at")
                order.save(update_fields=update_fields)

                UserAISubscription.objects.create(
                    user_id=order.user_id,
                    plan=order.ai_subscription_plan,
                    order=order,
                    status=UserAISubscription.Status.ACTIVE,
                    delivery_status=UserAISubscription.DeliveryStatus.DELIVERED,
                    activation_gmail=order.activation_gmail,
                    starts_at=now,
                    ends_at=now + timedelta(days=order.ai_subscription_plan.duration_days),
                )
            else:
                order.approved_at = None
                update_fields.append("approved_at")
                order.save(update_fields=update_fields)

            return Order.objects.select_related(
                "ai_subscription_plan",
                "ai_subscription_plan__product",
            ).get(id=order.id)
    except ObjectDoesNotExist:
        raise LookupError("order does not exist")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating order: {str(e)}")
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
