from catalog.infrastructure.models import ProductModel


class DjangoProductRepository:
    def get_by_id(self, product_id):
        try:
            return ProductModel.objects.get(id=product_id)
        except ProductModel.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
    
    def create(self, data):
        variants = data.pop("variants", [])
        product = ProductModel.objects.create(**data)
        for variant in variants:
            product.variants.create(**variant)
        return product

    def update(self, product, data):
        variants = data.pop("variants", None)
        for field, value in data.items():
            setattr(product, field, value)
        product.save()
        if variants is not None:
            product.variants.all().delete()
            for variant in variants:
                product.variants.create(**variant)
        return product
