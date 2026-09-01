from rest_framework import serializers


class OTPReceiveSerializer(serializers.Serializer):
    """
    Validates incoming SMS data.
    - 'phone_number': Customer/Recipient mobile number (or fallback to sender)
    - 'sender': SMS sender ID (e.g. 'IVAC_BD', 'from')
    - 'message': SMS text body (or 'text', 'body')
    """

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid data format. Expected a JSON object."]}
            )

        raw_phone = (
            data.get("phone_number")
            or data.get("customer_phone")
            or data.get("phone")
            or ""
        )
        raw_sender = (
            data.get("sender")
            or data.get("from")
            or ""
        )

        phone_number = str(raw_phone).strip() if raw_phone is not None else ""
        sender = str(raw_sender).strip() if raw_sender is not None else ""

        # Fallback: if no phone_number provided, use sender
        if not phone_number and sender:
            phone_number = sender

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

        if len(sender) > 64:
            errors["sender"] = ["Sender identifier exceeds maximum length of 64 characters."]

        if not message:
            errors["message"] = ["Message text is required."]
        elif len(message) > 2000:
            errors["message"] = ["Message exceeds maximum length of 2000 characters."]

        if errors:
            raise serializers.ValidationError(errors)

        return {
            "phone_number": phone_number,
            "sender": sender,
            "message": message,
        }


class OTPResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    sender = serializers.CharField(read_only=True)
    otp = serializers.CharField(read_only=True)


class OTPRecordResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    sender = serializers.CharField(read_only=True)
    otp = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
