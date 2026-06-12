from catalog.domain.services import validate_stock


class ProductService:
    def __init__(self, repository):
        self.repository = repository

    def create_product(self, data):
        validate_stock(data["stock"])
        return self.repository.create(data)

    def update_product(self, product, data):
        if "stock" in data:
            validate_stock(data["stock"])
        return self.repository.update(product, data)

    def reserve_stock(self, product_id, quantity):
        """Reserve stock for a product during checkout"""
        product = self.repository.get_by_id(product_id)
        if product.stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.stock}, Requested: {quantity}")
        
        product.stock -= quantity
        return self.repository.update(product, {"stock": product.stock})

    def release_stock(self, product_id, quantity):
        """Release reserved stock if order fails"""
        product = self.repository.get_by_id(product_id)
        product.stock += quantity
        return self.repository.update(product, {"stock": product.stock})

    def check_stock_availability(self, items):
        """Check if all items have sufficient stock"""
        for item in items:
            product = self.repository.get_by_id(item["product_id"])
            if product.stock < item["quantity"]:
                return False, f"Product {product.name} has insufficient stock"
        return True, "Stock available"
