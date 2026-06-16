from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework_simplejwt.views import TokenRefreshView


class AuthURLTests(SimpleTestCase):
    def test_token_refresh_route_is_available(self):
        match = resolve("/api/auth/token/refresh/")

        self.assertIs(match.func.view_class, TokenRefreshView)
