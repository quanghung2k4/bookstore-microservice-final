from payments.infrastructure.models import PaymentModel


class DjangoPaymentRepository:
    def create(self, data):
        return PaymentModel.objects.create(**data)

