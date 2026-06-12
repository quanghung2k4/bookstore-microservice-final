from django.db import models


class PaymentModel(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    order_id = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-id"]

