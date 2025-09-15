from django.db import models
from accounts.models import User
from products.models import Product, ProductAttribute


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="products"
    )
    product_attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
