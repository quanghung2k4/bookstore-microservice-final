from rest_framework import serializers
from .models import ShippingAddress


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["id", "order_id", "user_id", "full_name", "phone", "address", "city", "note", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]
