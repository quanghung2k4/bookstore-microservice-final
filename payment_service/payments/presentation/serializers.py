from rest_framework import serializers

from payments.infrastructure.models import PaymentModel


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = ["id", "order_id", "amount", "method", "status", "transaction_id", "created_at"]
        read_only_fields = ["id", "status", "transaction_id", "created_at"]

