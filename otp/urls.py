from django.urls import path

from .views import OTPReceiveAPIView


urlpatterns = [
    path("otp/", OTPReceiveAPIView.as_view(), name="otp-receive"),
]
