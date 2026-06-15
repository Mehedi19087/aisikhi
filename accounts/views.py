import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core import signing
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserResponseSerializer
from .services import get_or_create_google_user


logger = logging.getLogger("accounts.views")
SUPPORTED_AUTH_PLATFORMS = {"web", "mobile"}
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def _error_response(message, status_code=status.HTTP_400_BAD_REQUEST, extra=None):
    payload = {"error": message}
    if extra:
        payload.update(extra)
    return Response(payload, status=status_code)


def _get_google_redirect_uri(request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if redirect_uri:
        return redirect_uri
    return request.build_absolute_uri(reverse("google-callback"))


def _encode_oauth_state(platform):
    selected_platform = platform if platform in SUPPORTED_AUTH_PLATFORMS else "web"
    return signing.dumps({"platform": selected_platform}, salt="google-oauth-state")


def _decode_oauth_state(state):
    if not state:
        raise ValueError("OAuth state is missing")

    try:
        payload = signing.loads(
            state,
            salt="google-oauth-state",
            max_age=600,
        )
    except signing.BadSignature:
        logger.warning("Invalid Google OAuth state received")
        raise ValueError("OAuth state is invalid or expired")

    platform = payload.get("platform", "web")
    if platform not in SUPPORTED_AUTH_PLATFORMS:
        platform = "web"
    return {"platform": platform}


def _build_redirect_url(base_url, access_token, refresh_token):
    redirect_url_parts = base_url.split("#", 1)
    base_part = redirect_url_parts[0]
    hash_part = f"#{redirect_url_parts[1]}" if len(redirect_url_parts) > 1 else ""

    query_parts = base_part.split("?", 1)
    redirect_base = query_parts[0]
    existing_params = dict(parse_qsl(query_parts[1])) if len(query_parts) > 1 else {}
    existing_params.update({"access": access_token, "refresh": refresh_token})

    return f"{redirect_base}?{urlencode(existing_params)}{hash_part}"


def _post_form(url, data):
    encoded_data = urlencode(data).encode("utf-8")
    request = Request(
        url,
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url, headers):
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


class GoogleAuthURLView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        if not settings.GOOGLE_CLIENT_ID:
            return _error_response(
                "GOOGLE_CLIENT_ID missing",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        platform = (request.GET.get("platform") or "web").strip().lower()
        if platform not in SUPPORTED_AUTH_PLATFORMS:
            platform = "web"

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": _get_google_redirect_uri(request),
            "response_type": "code",
            "scope": "openid email profile",
            "state": _encode_oauth_state(platform),
            "access_type": "online",
            "prompt": "select_account",
        }
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
        return Response({"auth_url": auth_url})


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return _error_response("No code provided by Google")

        try:
            state_payload = _decode_oauth_state(request.GET.get("state"))
        except ValueError as e:
            return _error_response(str(e), status.HTTP_400_BAD_REQUEST)

        platform = state_payload.get("platform", "web")
        redirect_uri = _get_google_redirect_uri(request)

        missing_settings = [
            name
            for name, value in (
                ("GOOGLE_CLIENT_ID", settings.GOOGLE_CLIENT_ID),
                ("GOOGLE_CLIENT_SECRET", settings.GOOGLE_CLIENT_SECRET),
                ("FRONTEND_GOOGLE_REDIRECT_URL", settings.FRONTEND_GOOGLE_REDIRECT_URL),
            )
            if not value
        ]
        if platform == "mobile" and not settings.MOBILE_GOOGLE_REDIRECT_URL:
            missing_settings.append("MOBILE_GOOGLE_REDIRECT_URL")

        if missing_settings:
            return _error_response(
                f"Server configuration incomplete. Missing: {', '.join(missing_settings)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            token_data = _post_form(
                GOOGLE_TOKEN_URL,
                {
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        except HTTPError as exc:
            logger.error("Google token exchange failed: status=%s", exc.code)
            return _error_response(
                "Google token exchange failed",
                status.HTTP_400_BAD_REQUEST,
                {"provider_status": exc.code},
            )
        except URLError as exc:
            logger.exception("Could not reach Google token service: %s", exc)
            return _error_response(
                "Could not reach Google token service",
                status.HTTP_502_BAD_GATEWAY,
            )

        google_access_token = token_data.get("access_token")
        if not google_access_token:
            return _error_response("Google did not return an access token")

        try:
            user_data = _get_json(
                GOOGLE_USERINFO_URL,
                {"Authorization": f"Bearer {google_access_token}"},
            )
        except HTTPError as exc:
            logger.error("Google userinfo failed: status=%s", exc.code)
            return _error_response(
                "Failed to fetch Google user info",
                status.HTTP_400_BAD_REQUEST,
                {"provider_status": exc.code},
            )
        except URLError as exc:
            logger.exception("Could not reach Google user profile service: %s", exc)
            return _error_response(
                "Could not reach Google user profile service",
                status.HTTP_502_BAD_GATEWAY,
            )

        try:
            user, created = get_or_create_google_user(user_data)
        except ValueError as e:
            return _error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Could not finish Google sign-in")
            return _error_response(
                "Could not finish sign-in for this account",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        logger.info(
            "Google user authenticated | user_id=%s | email=%s | created=%s",
            user.id,
            user.email,
            created,
        )

        redirect_target = (
            settings.MOBILE_GOOGLE_REDIRECT_URL
            if platform == "mobile"
            else settings.FRONTEND_GOOGLE_REDIRECT_URL
        )
        if redirect_target:
            return redirect(
                _build_redirect_url(
                    redirect_target,
                    access_token=str(access_token),
                    refresh_token=str(refresh),
                )
            )

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh),
                "user": UserResponseSerializer(user).data,
            }
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserResponseSerializer(request.user).data)
