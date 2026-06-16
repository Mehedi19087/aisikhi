from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import AISubscriptionPlan, Product
from subscriptions.models import UserAISubscription

from .models import Order


class AdminOrderStatusTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="customer@example.com",
            password="password",
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password",
            is_staff=True,
        )
        self.product = Product.objects.create(
            name="ChatGPT Plus",
            slug="chatgpt-plus",
        )
        self.plan = AISubscriptionPlan.objects.create(
            product=self.product,
            account_type=AISubscriptionPlan.AccountType.PERSONAL,
            duration_days=30,
            price="1200.00",
            title="ChatGPT Plus Personal",
        )

    def create_order(self):
        return Order.objects.create(
            user=self.user,
            ai_subscription_plan=self.plan,
            amount=self.plan.price,
            payment_method=Order.PaymentMethod.BKASH,
            transaction_id="TXN123456",
            activation_gmail="activate@example.com",
        )

    def test_admin_can_approve_order_and_activate_subscription(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            f"/api/admin/orders/{order.id}/",
            {"status": Order.Status.APPROVED, "admin_note": "verified"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.APPROVED)
        self.assertEqual(order.admin_note, "verified")
        self.assertIsNotNone(order.approved_at)

        subscription = UserAISubscription.objects.get(order=order)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.status, UserAISubscription.Status.ACTIVE)
        self.assertEqual(
            subscription.delivery_status,
            UserAISubscription.DeliveryStatus.DELIVERED,
        )
        self.assertEqual(subscription.activation_gmail, order.activation_gmail)
        self.assertIsNotNone(subscription.starts_at)
        self.assertIsNotNone(subscription.ends_at)

    def test_admin_can_reject_order_without_creating_subscription(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            f"/api/admin/orders/{order.id}/",
            {"status": Order.Status.REJECTED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.REJECTED)
        self.assertFalse(UserAISubscription.objects.filter(order=order).exists())

    def test_non_admin_cannot_update_order_status(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            f"/api/admin/orders/{order.id}/",
            {"status": Order.Status.APPROVED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
