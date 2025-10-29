from django.db import models

from products.models import Product
from users.models import User


class Review(models.Model):
    RATING_CHOICES = [
        (1, "ONE"),
        (2, "TWO"),
        (3, "THREE"),
        (4, "FOUR"),
        (5, "FIVE"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.CharField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"review of {self.product} by {self.user}"
