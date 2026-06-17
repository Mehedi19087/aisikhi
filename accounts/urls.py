from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CurrentUserView, GoogleAuthURLView, GoogleCallbackView


urlpatterns = [
    path("auth/google/url/", GoogleAuthURLView.as_view(), name="google-auth-url"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
]
