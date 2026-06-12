from carts.infrastructure.models import CartItemModel, CartModel


class DjangoCartRepository:
    def get_or_create_cart(self, user_id):
        cart, _ = CartModel.objects.get_or_create(user_id=user_id)
        return cart

    def add_item(self, cart, product_id, quantity, price):
        item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={"quantity": quantity, "price": price},
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    def update_item(self, item, quantity):
        item.quantity = quantity
        item.save()
        return item

