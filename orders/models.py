from datetime import timedelta
from django.db import models
from users.models import User
from core.utils.order_id_gen import unique_id
from cart.models import CartItem
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("delivered", "Delivered"),
    ]
    id = models.CharField(
        default=unique_id, unique=True, primary_key=True, max_length=20
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orders")
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="pending")
    discount = models.ForeignKey("Discount", on_delete=models.DO_NOTHING, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Order: {self.id}"

    @property
    def total_amount(self):
        total = 0
        for item in self.order_items.all():
            total += item.item.product.price * item.quantity
        return total


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    # fixed the multiple items per order
    # only one item per order
    class Meta:
        unique_together = ["order", "item"]
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} x {self.item.product.name} in Order {self.order.id}"

    @property
    def total_price(self):
        return self.item.product.price * self.quantity


from .validators import percentage_validator
class Discount(models.Model):
    code_name = models.CharField(max_length=100, primary_key=True, unique=True)
    user_count = models.PositiveBigIntegerField()
    percentage_off = models.IntegerField(validators=[percentage_validator])
    from_date = models.DateTimeField(default=timezone.now)
    to_date = models.DateTimeField(default=(timezone.now() + timedelta(days=7)))
    
    @property
    def is_active(self):
        now = timezone.now
        return self.from_date >= now >= self.to_date

    def __str__(self):
        return f"{self.code_name}"
    
