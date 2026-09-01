from rest_framework import serializers


class OTPReceiveSerializer(serializers.Serializer):
    """
    Validates incoming SMS data. Supports standard fields ('phone_number', 'message')
    as well as Android SMS Gateway Webhook aliases ('from', 'sender', 'phone', 'text', 'body').
    """

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid data format. Expected a JSON object."]}
            )

        raw_phone = (
            data.get("phone_number")
            or data.get("phone")
            or data.get("from")
            or data.get("sender")
            or ""
        )
        phone_number = str(raw_phone).strip() if raw_phone is not None else ""

        raw_message = (
            data.get("message")
            or data.get("text")
            or data.get("body")
            or ""
        )
        message = str(raw_message).strip() if raw_message is not None else ""

        errors = {}
        if not phone_number:
            errors["phone_number"] = ["Phone number or sender identifier is required."]
        elif len(phone_number) > 64:
            errors["phone_number"] = ["Phone number exceeds maximum length of 64 characters."]

        if not message:
            errors["message"] = ["Message text is required."]
        elif len(message) > 2000:
            errors["message"] = ["Message exceeds maximum length of 2000 characters."]

        if errors:
            raise serializers.ValidationError(errors)

        return {
            "phone_number": phone_number,
            "message": message,
        }


class OTPResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    otp = serializers.CharField(read_only=True)
