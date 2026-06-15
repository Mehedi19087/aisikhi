from django.urls import path

from .views import CurrentUserView, GoogleAuthURLView, GoogleCallbackView


urlpatterns = [
    path("auth/google/url/", GoogleAuthURLView.as_view(), name="google-auth-url"),
    path("auth/google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
]
