from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ShippingAddress
from .serializers import ShippingAddressSerializer


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        order_id = self.request.query_params.get("order_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs

    @action(detail=False, methods=["patch"], url_path="by-order/(?P<order_id>[^/.]+)")
    def update_by_order(self, request, order_id=None):
        try:
            obj = ShippingAddress.objects.get(order_id=order_id)
        except ShippingAddress.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
