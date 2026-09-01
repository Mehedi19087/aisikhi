from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OTPReceiveSerializer
from .services import process_otp_sms


class OTPReceiveAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        message = serializer.validated_data["message"]

        # Check if this is a test ping from the Android app's "TEST" button
        is_test = (
            "test" in phone_number.lower()
            or "test" in message.lower()
            or "%text%" in message
            or "%from%" in phone_number
        )

        otp_record, otp = process_otp_sms(
            phone_number=phone_number,
            message=message,
        )

        if not otp:
            if is_test:
                return Response(
                    {
                        "success": True,
                        "phone_number": phone_number,
                        "otp": "TEST_OK",
                        "message": "Webhook connection test successful.",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "success": False,
                    "otp": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "phone_number": otp_record.phone_number,
                "otp": otp_record.otp,
            },
            status=status.HTTP_200_OK,
        )
