from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AdminUpdateOrderStatusSerializer,
    CreateAISubscriptionOrderSerializer,
    OrderResponseSerializer,
    UpdateOrderSerializer,
)
from .services import (
    cancel_user_order,
    create_ai_subscription_order,
    get_user_order,
    get_user_orders,
    update_order_status_by_admin,
    update_user_order,
)


class CreateAISubscriptionOrderApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateAISubscriptionOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = create_ai_subscription_order(
                request.user.id,
                serializer.validated_data,
            )
            result = OrderResponseSerializer(order)
            return Response(
                {
                    "message": "AI subscription order created successfully",
                    "data": result.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyOrderListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = get_user_orders(request.user.id)
            result = OrderResponseSerializer(orders, many=True)
            return Response(
                {
                    "message": "Orders fetched successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyOrderDetailsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            order = get_user_order(id, request.user.id)
            serializer = OrderResponseSerializer(order)
            return Response(
                {
                    "message": "Order fetched successfully",
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

    def put(self, request, id):
        serializer = UpdateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = update_user_order(id, request.user.id, serializer.validated_data)
            result = OrderResponseSerializer(order)
            return Response(
                {
                    "message": "Order updated successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except LookupError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, id):
        try:
            cancel_user_order(id, request.user.id)
            return Response(
                {
                    "message": "Order cancelled successfully",
                },
                status=status.HTTP_200_OK,
            )
        except LookupError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminOrderDetailsApiView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        serializer = AdminUpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = update_order_status_by_admin(id, serializer.validated_data)
            result = OrderResponseSerializer(order)
            return Response(
                {
                    "message": "Order updated successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except LookupError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
