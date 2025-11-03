from django.dispatch import receiver
from django.db.models.signals import post_save
from models import Order, OrderItems

@receiver(post_save, sender=Order)
def update_product_quantity(sender, instance, created, **kwargs):
    if created and instance.status=="pending": 
        print(instance.order_items.objects())