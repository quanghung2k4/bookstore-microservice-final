from django.db import models


class OrderModel(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )

    user_id = models.PositiveIntegerField()
    cart_id = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-id"]


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=20)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"
        ordering = ["id"]

