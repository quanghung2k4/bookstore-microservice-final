from django.db import models

class UserBehaviorEvent(models.Model):
	user_id = models.CharField(max_length=128, db_index=True)
	product_id = models.CharField(max_length=128, db_index=True)
	action = models.CharField(max_length=64)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["user_id", "created_at"]),
			models.Index(fields=["user_id", "product_id"]),
		]

	def __str__(self) -> str:
		return f"{self.user_id} {self.action} {self.product_id}"
