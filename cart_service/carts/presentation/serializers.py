from rest_framework import serializers

from carts.infrastructure.models import CartItemModel, CartModel


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItemModel
        fields = ["id", "product_id", "quantity", "price", "total_price", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_total_price(self, obj):
        return obj.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = CartModel
        fields = ["id", "user_id", "items", "total_amount", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # Allow POST even if cart already exists (handled in view via get_or_create)
        validators = []
    
    def get_total_amount(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())


class AddItemSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=20)
    quantity = serializers.IntegerField(min_value=1)

