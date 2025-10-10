from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
from core.utils.order_id_gen import unique_id

User = get_user_model()

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="payments")
    id = models.CharField(
        max_length=20, primary_key=True, default=unique_id, unique=True
    )
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True, null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.order.id} - ${self.amount}"