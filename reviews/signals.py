from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review
from products.models import Product

@receiver(post_save, sender=Review) 
def update_product_rating(sender, instance, **kwargs):
    """update product average rating and review count when a review is added/deleted"""
    product = instance.product

    stats = product.reviews.aggregate(
        avg_rating=Avg("rating"),
        review_count = Count("id")
    )

    # I'll have to update the product fields 
    product.average_rating = stats["avg_rating"]
    product.review_count = stats["review_count"]
    product.save(update_fields=["average_rating","review_count"])