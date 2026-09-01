from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import OTPRecord
from .services import extract_otp


class OTPExtractionServiceTests(TestCase):
    def test_various_otp_messages(self):
        test_cases = [
            # Spelled-out number words (IVAC BD format)
            (
                "(IVACBD) For security, type the following sequence when prompted Seven-One-Nine-Three-Two-One .",
                "719321",
            ),
            (
                "(IVAC_BD) For security type the sequence Seven-One-Nine-Three-Two-One",
                "719321",
            ),
            (
                "type the following sequence when prompted seven one nine three two one",
                "719321",
            ),
            (
                "Seven, One, Nine, Three, Two, One",
                "719321",
            ),
            (
                "Four-Five-Six-Seven",
                "4567",
            ),
            (
                "Zero-One-Two-Three-Four-Five-Six-Seven",
                "01234567",
            ),
            # Standard numeric OTPs
            ("Your OTP is 482931", "482931"),
            ("Verification code: 739201", "739201"),
            ("Use 8392 to continue", "8392"),
            ("Your visa verification code is 739201", "739201"),
            ("739201 is your code", "739201"),
            ("Code is 123456.", "123456"),
            ("Google code: G-789012", "789012"),
            ("Your 8-digit OTP is 12345678", "12345678"),
            ("Just 4 digits 9081", "9081"),
            # Bengali digits
            ("আপনার ওটিপি হলো ৭৩৯২০১", "739201"),
            # Invalid or missing OTP
            ("No digits here", None),
            ("Too short 123", None),
            ("Too long 123456789", None),
            ("", None),
            (None, None),
        ]

        for message, expected in test_cases:
            with self.subTest(message=message):
                self.assertEqual(extract_otp(message), expected)


class OTPReceiveAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("otp-receive")

    def test_receive_otp_successfully_with_standard_numeric(self):
        payload = {
            "phone_number": "01712345678",
            "message": "Your verification code is 739201",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "success": True,
                "phone_number": "01712345678",
                "sender": "",
                "otp": "739201",
            },
        )

        record = OTPRecord.objects.filter(phone_number="01712345678").first()
        self.assertIsNotNone(record)
        self.assertEqual(record.otp, "739201")

    def test_receive_ivac_bd_spelled_out_otp_successfully(self):
        # Test exact IVAC BD SMS payload
        payload = {
            "phone_number": "IVAC_BD",
            "message": "(IVACBD) For security, type the following sequence when prompted Seven-One-Nine-Three-Two-One .",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "success": True,
                "phone_number": "IVAC_BD",
                "sender": "",
                "otp": "719321",
            },
        )

        record = OTPRecord.objects.filter(phone_number="IVAC_BD").first()
        self.assertIsNotNone(record)
        self.assertEqual(record.otp, "719321")

    def test_receive_webhook_payload_with_from_and_text_aliases(self):
        # Testing payload format sent by bogkonstantin/android_income_sms_gateway_webhook
        payload = {
            "from": "IVAC_BD",
            "text": "(IVACBD) For security, type the following sequence when prompted Seven-One-Nine-Three-Two-One .",
            "sim": "1",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "success": True,
                "phone_number": "IVAC_BD",
                "sender": "IVAC_BD",
                "otp": "719321",
            },
        )

    def test_android_app_test_button_ping_returns_200_ok(self):
        # When Android app presses "TEST", it sends test strings
        payload = {
            "from": "TestSender",
            "text": "Test message from Android SMS Gateway",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["otp"], "TEST_OK")

    def test_receive_otp_fails_when_no_otp_in_non_test_message(self):
        payload = {
            "phone_number": "01712345678",
            "message": "Welcome to our service without any code.",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "success": False,
                "otp": None,
            },
        )
        self.assertEqual(OTPRecord.objects.count(), 0)

    def test_validation_errors_for_missing_or_empty_fields(self):
        # Missing phone / sender
        response = self.client.post(
            self.url,
            {"message": "Code is 123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing message
        response = self.client.post(
            self.url,
            {"phone_number": "01712345678"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Empty phone
        response = self.client.post(
            self.url,
            {"phone_number": "   ", "message": "Code is 123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Empty message
        response = self.client.post(
            self.url,
            {"phone_number": "01712345678", "message": "   "},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_recent_request_reuses_record(self):
        payload = {
            "phone_number": "01712345678",
            "message": "Your verification code is 739201",
        }

        # First request creates record
        response1 = self.client.post(self.url, payload, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(OTPRecord.objects.count(), 1)

        # Immediate retry with same phone and message
        response2 = self.client.post(self.url, payload, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(OTPRecord.objects.count(), 1)

    def test_get_otp_list_returns_records(self):
        OTPRecord.objects.create(phone_number="01712345678", otp="123456")
        OTPRecord.objects.create(phone_number="IVAC_BD", otp="719321")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["otp"], "719321")

    def test_receive_customer_phone_and_sender_together(self):
        payload = {
            "phone_number": "01712345678",
            "from": "IVAC_BD",
            "text": "(IVACBD) For security, type the following sequence when prompted Seven-One-Nine-Three-Two-One .",
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone_number"], "01712345678")
        self.assertEqual(response.data["sender"], "IVAC_BD")
        self.assertEqual(response.data["otp"], "719321")

        record = OTPRecord.objects.get(phone_number="01712345678")
        self.assertEqual(record.sender, "IVAC_BD")
        self.assertEqual(record.otp, "719321")


