import hashlib
import logging

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


logger = logging.getLogger("accounts.auth")


def _fingerprint(value):
    if not value:
        return "missing"
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]


class LoggingJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            logger.warning(
                "JWT header present but raw token missing | auth_header=%s | signing_key_fp=%s",
                header[:32],
                _fingerprint(settings.SIMPLE_JWT.get("SIGNING_KEY")),
            )
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except InvalidToken as exc:
            logger.error(
                "JWT validation failed: %s | signing_key_fp=%s | algorithm=%s | token_prefix=%s",
                exc,
                _fingerprint(settings.SIMPLE_JWT.get("SIGNING_KEY")),
                settings.SIMPLE_JWT.get("ALGORITHM"),
                raw_token[:16].decode("utf-8", errors="ignore"),
            )
            raise

        logger.info(
            "JWT accepted | path=%s | user_id=%s",
            getattr(request, "path", ""),
            getattr(user, "id", None),
        )
        return (user, validated_token)
