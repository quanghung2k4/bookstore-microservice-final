from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.application.use_cases import CartService
from carts.infrastructure.clients import ProductClient, UserClient
from carts.infrastructure.models import CartItemModel, CartModel
from carts.infrastructure.repositories import DjangoCartRepository
from carts.presentation.serializers import AddItemSerializer, CartItemSerializer, CartSerializer


def build_service():
    return CartService(DjangoCartRepository(), ProductClient(), UserClient())


class CartViewSet(viewsets.ModelViewSet):
    queryset = CartModel.objects.prefetch_related("items").all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"user_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        cart = build_service().create_cart(int(user_id))
        return Response(self.get_serializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="items")
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = build_service().add_item(cart, **serializer.validated_data)
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"], url_path="clear")
    def clear(self, request, pk=None):
        """Clear all items from cart"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.GenericViewSet):
    queryset = CartItemModel.objects.all()
    serializer_class = CartItemSerializer

    def partial_update(self, request, pk=None):
        item = self.get_object()
        item = build_service().update_item(item, int(request.data.get("quantity")))
        return Response(self.get_serializer(item).data)

    def destroy(self, request, pk=None):
        item = self.get_object()
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

