from orders.infrastructure.models import OrderItemModel, OrderModel


class DjangoOrderRepository:
    def create_order(self, user_id, cart_id, items, total):
        order = OrderModel.objects.create(user_id=user_id, cart_id=cart_id, total_price=total)
        for item in items:
            OrderItemModel.objects.create(order=order, **item)
        return order

    def attach_payment(self, order, payment):
        order.payment_reference = payment["transaction_id"]
        if payment["status"] == "paid":
            order.status = "paid"
        order.save()
        return order

