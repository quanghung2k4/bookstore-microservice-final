from payments.domain.services import generate_transaction_id


class PaymentService:
    def __init__(self, repository):
        self.repository = repository

    def create_payment(self, data):
        data["transaction_id"] = generate_transaction_id()
        data["status"] = "paid" if data["method"] == "cod" else "pending"
        return self.repository.create(data)

