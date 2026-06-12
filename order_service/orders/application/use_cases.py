from orders.domain.services import calculate_total


class CheckoutService:
    def __init__(self, repository, cart_client, product_client, user_client, payment_client, ai_client=None):
        self.repository = repository
        self.cart_client = cart_client
        self.product_client = product_client
        self.user_client = user_client
        self.payment_client = payment_client
        self.ai_client = ai_client

    def checkout(self, user_id, cart_id):
        # Validate user exists
        self.user_client.ensure_user(user_id)
        
        # Get cart data
        cart = self.cart_client.get_cart(cart_id)
        if not cart.get("items"):
            raise ValueError("Cart is empty")
        
        # Prepare items for stock check
        stock_items = [{"product_id": item["product_id"], "quantity": item["quantity"]} 
                      for item in cart["items"]]
        
        # Check stock availability
        stock_check = self.product_client.check_stock(stock_items)
        if not stock_check["available"]:
            raise ValueError(stock_check["message"])
        
        # Reserve stock for all items
        reserved_items = []
        try:
            items = []
            for item in cart["items"]:
                # Reserve stock
                self.product_client.reserve_stock(item["product_id"], item["quantity"])
                reserved_items.append(item)
                
                # Get product details
                product = self.product_client.get_product(item["product_id"])
                items.append({
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "unit_price": product["price"],
                    "product_name": product["name"],
                })
            
            # Calculate total
            total = calculate_total(items)
            
            # Create order
            order = self.repository.create_order(user_id, cart_id, items, total)
            
            # Create payment
            payment = self.payment_client.create_payment(order.id, total)
            self.repository.attach_payment(order, payment)

            # Emit purchase events to AI service (best-effort)
            if self.ai_client is not None:
                for item in items:
                    try:
                        self.ai_client.track_purchase(
                            user_id=user_id,
                            product_id=item.get("product_id"),
                            quantity=item.get("quantity", 1),
                        )
                    except Exception:
                        pass
            
            # Clear cart after successful checkout
            self.cart_client.clear_cart(cart_id)
            
            return order
            
        except Exception as e:
            # Release reserved stock if anything fails
            for item in reserved_items:
                try:
                    self.product_client.release_stock(item["product_id"], item["quantity"])
                except:
                    pass  # Log error but don't fail the rollback
            raise e

