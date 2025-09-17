from django.db import models
from accounts.models import User
from core.utils.order_id_gen import unique_id
from cart.models import CartItem


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("delivered", "Delivered"),
    ]
    id = models.CharField(default=unique_id, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orders")
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)

    def __str__(self):
        return f"Order: {self.id}"


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.product.name} in Order {self.order.id}"
