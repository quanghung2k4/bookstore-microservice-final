from carts.domain.services import validate_quantity


class CartService:
    def __init__(self, repository, product_client, user_client):
        self.repository = repository
        self.product_client = product_client
        self.user_client = user_client

    def create_cart(self, user_id):
        return self.repository.get_or_create_cart(user_id)

    def add_item(self, cart, product_id, quantity):
        validate_quantity(quantity)
        product_data = self.product_client.ensure_product(product_id)
        price = product_data.get('price', 0)
        return self.repository.add_item(cart, product_id, quantity, price)

    def update_item(self, item, quantity):
        validate_quantity(quantity)
        return self.repository.update_item(item, quantity)

