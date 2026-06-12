from rest_framework import serializers

from orders.infrastructure.models import OrderItemModel, OrderModel


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemModel
        fields = ["id", "product_id", "product_name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "user_id",
            "cart_id",
            "total_price",
            "status",
            "payment_reference",
            "items",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    cart_id = serializers.IntegerField()

