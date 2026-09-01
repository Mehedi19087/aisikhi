from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OTPReceiveSerializer, OTPRecordResponseSerializer
from .services import get_latest_otps, process_otp_sms


class OTPReceiveAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieves the latest OTP records for display in frontend dashboards.
        Supports query params:
        - ?limit=20 (default 20, max 100)
        - ?phone_number=017... (optional filter)
        - ?sender=IVAC_BD (optional filter)
        """
        limit_param = request.query_params.get("limit", 20)
        try:
            limit = min(max(int(limit_param), 1), 100)
        except (ValueError, TypeError):
            limit = 20

        phone_filter = request.query_params.get("phone_number", "").strip()
        sender_filter = request.query_params.get("sender", "").strip()

        records = get_latest_otps(limit=limit)
        if phone_filter:
            records = records.filter(phone_number__icontains=phone_filter)
        if sender_filter:
            records = records.filter(sender__icontains=sender_filter)

        serializer = OTPRecordResponseSerializer(records, many=True)
        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = OTPReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        sender = serializer.validated_data.get("sender", "")
        message = serializer.validated_data["message"]

        # Check if this is a test ping from the Android app's "TEST" button
        is_test = (
            "test" in phone_number.lower()
            or "test" in sender.lower()
            or "test" in message.lower()
            or "%text%" in message
            or "%from%" in phone_number
        )

        otp_record, otp = process_otp_sms(
            phone_number=phone_number,
            sender=sender,
            message=message,
        )

        if not otp:
            if is_test:
                return Response(
                    {
                        "success": True,
                        "phone_number": phone_number,
                        "sender": sender,
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
                "sender": otp_record.sender,
                "otp": otp_record.otp,
            },
            status=status.HTTP_200_OK,
        )
