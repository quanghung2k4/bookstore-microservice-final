from django.db import models


class ShippingAddress(models.Model):
    order_id = models.PositiveIntegerField(unique=True)
    user_id = models.PositiveIntegerField()
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    address = models.TextField()
    city = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("shipping", "Shipping"), ("delivered", "Delivered")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipping_addresses"
        ordering = ["-id"]
