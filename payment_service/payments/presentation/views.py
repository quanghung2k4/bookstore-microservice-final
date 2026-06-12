from rest_framework import status, viewsets
from rest_framework.response import Response

from payments.application.use_cases import PaymentService
from payments.infrastructure.models import PaymentModel
from payments.infrastructure.repositories import DjangoPaymentRepository
from payments.presentation.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = PaymentModel.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = PaymentService(DjangoPaymentRepository()).create_payment(dict(serializer.validated_data))
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)

