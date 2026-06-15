from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserAISubscriptionResponseSerializer
from .services import (
    get_active_user_ai_subscription,
    get_user_ai_subscription,
    get_user_ai_subscriptions,
)


class MyAISubscriptionListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subscriptions = get_user_ai_subscriptions(request.user.id)
            result = UserAISubscriptionResponseSerializer(subscriptions, many=True)
            return Response(
                {
                    "message": "AI subscriptions fetched successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyActiveAISubscriptionApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subscription = get_active_user_ai_subscription(request.user.id)
            if subscription is None:
                return Response(
                    {"error": "active AI subscription not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = UserAISubscriptionResponseSerializer(subscription)
            return Response(
                {
                    "message": "Active AI subscription fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyAISubscriptionDetailsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            subscription = get_user_ai_subscription(id, request.user.id)
            serializer = UserAISubscriptionResponseSerializer(subscription)
            return Response(
                {
                    "message": "AI subscription fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except LookupError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
