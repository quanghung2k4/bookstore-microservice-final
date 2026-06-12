from django.contrib.auth.models import AbstractUser
from django.db import models


class UserModel(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "users"
        ordering = ["id"]

