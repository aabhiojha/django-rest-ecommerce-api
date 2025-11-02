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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"review of {self.product.name} by {self.user.email}"


class Reply(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    reviewer = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    message = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=["-created_at"]
        unique_together = ("seller", "reviewer")
        verbose_name_plural = "replies"

    def __str__(self):
        return f"Reply by {self.seller.email} to {self.reviewer.user.email}"