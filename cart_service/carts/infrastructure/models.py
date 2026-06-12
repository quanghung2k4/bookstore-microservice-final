from django.db import models


class CartModel(models.Model):
    user_id = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"
        ordering = ["id"]


class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ("cart", "product_id")
        ordering = ["id"]

