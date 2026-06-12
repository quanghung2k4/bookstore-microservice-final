from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.application.use_cases import CheckoutService
from orders.infrastructure.clients import AIClient, CartClient, PaymentClient, ProductClient, UserClient
from orders.infrastructure.models import OrderModel
from orders.infrastructure.repositories import DjangoOrderRepository
from orders.presentation.serializers import CheckoutSerializer, OrderSerializer


def build_service():
    return CheckoutService(
        DjangoOrderRepository(),
        CartClient(),
        ProductClient(),
        UserClient(),
        PaymentClient(),
        ai_client=AIClient(),
    )


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderModel.objects.prefetch_related("items").all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = build_service().checkout(**serializer.validated_data)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

