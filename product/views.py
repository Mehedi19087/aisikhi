from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, IsAdminUser

from .serializers import (
    AISubscriptionPlanCreateSerializer,
    AISubscriptionPlanResponseSerializer,
    AISubscriptionPlanUpdateSerializer,
    ProductCreateSerializer,
    ProductResponseSerializer,
    ProductUpdateSerializer,
)
from .services import (
    create_ai_subscription_plan,
    create_product,
    delete_ai_subscription_plan,
    delete_product,
    get_ai_subscription_plan,
    get_all_ai_subscription_plans,
    get_all_products,
    get_product,
    update_ai_subscription_plan,
    update_product,
)


class ProductListCreateApiView(APIView):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdminUser()]

    def get(self, request):
        try:
            products = get_all_products()
            result = ProductResponseSerializer(products, many=True)
            return Response(
                {
                    "message": "Products fetched successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = create_product(serializer.validated_data)
            result = ProductResponseSerializer(product)
            return Response(
                {
                    "message": "Product created successfully",
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


class ProductDetailsApiView(APIView):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdminUser()]

    def get(self, request, id):
        try:
            product = get_product(id)
            serializer = ProductResponseSerializer(product)
            return Response(
                {
                    "message": "Product fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except LookupError as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, id):
        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = update_product(id, serializer.validated_data)
            result = ProductResponseSerializer(product)
            return Response(
                {
                    "message": "Product updated successfully",
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
            delete_product(id)
            return Response(
                {
                    "message": "Product deleted successfully",
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


class AISubscriptionPlanListCreateApiView(APIView):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdminUser()]

    def get(self, request):
        try:
            plans = get_all_ai_subscription_plans()
            result = AISubscriptionPlanResponseSerializer(plans, many=True)
            return Response(
                {
                    "message": "AI subscription plans fetched successfully",
                    "data": result.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        serializer = AISubscriptionPlanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan = create_ai_subscription_plan(serializer.validated_data)
            result = AISubscriptionPlanResponseSerializer(plan)
            return Response(
                {
                    "message": "AI subscription plan created successfully",
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


class AISubscriptionPlanDetailsApiView(APIView):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdminUser()]

    def get(self, request, id):
        try:
            plan = get_ai_subscription_plan(id)
            serializer = AISubscriptionPlanResponseSerializer(plan)
            return Response(
                {
                    "message": "AI subscription plan fetched successfully",
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
        serializer = AISubscriptionPlanUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan = update_ai_subscription_plan(id, serializer.validated_data)
            result = AISubscriptionPlanResponseSerializer(plan)
            return Response(
                {
                    "message": "AI subscription plan updated successfully",
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
            delete_ai_subscription_plan(id)
            return Response(
                {
                    "message": "AI subscription plan deleted successfully",
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
