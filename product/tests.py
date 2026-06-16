from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AISubscriptionPlan, Product


class ProductPermissionTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            email="admin@example.com",
            password="password",
            is_staff=True,
        )

    def test_product_write_requires_admin_user(self):
        payload = {
            "name": "ChatGPT Plus",
            "slug": "chatgpt-plus",
            "description": "AI tool subscription",
        }

        public_response = self.client.post("/api/products/", payload, format="json")
        self.assertIn(
            public_response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        self.client.force_authenticate(user=self.admin)
        admin_response = self.client.post("/api/products/", payload, format="json")
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)

    def test_product_read_stays_public(self):
        Product.objects.create(name="Canva Pro", slug="canva-pro")

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["slug"], "canva-pro")

    def test_ai_subscription_plan_write_requires_admin_user(self):
        product = Product.objects.create(name="Gemini Advanced", slug="gemini-advanced")
        payload = {
            "product": product.id,
            "account_type": AISubscriptionPlan.AccountType.PERSONAL,
            "duration_days": 30,
            "price": "1000.00",
            "title": "Gemini Advanced Personal",
        }

        public_response = self.client.post(
            "/api/ai-subscription-plans/",
            payload,
            format="json",
        )
        self.assertIn(
            public_response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        self.client.force_authenticate(user=self.admin)
        admin_response = self.client.post(
            "/api/ai-subscription-plans/",
            payload,
            format="json",
        )
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
