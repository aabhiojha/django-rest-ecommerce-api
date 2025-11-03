from django.db import models
from users.models import User
from products.models import Product, ProductVarient

# to do
# show the total no of items in cart
# total cost of an item in accordance to the quantity ie subtotal
# tax as well
# total cost of the entire cart
# maybe later: discounts?


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.cart_items.all())

    @property
    def total(self):
        # getall items in the cart and then sum
        return sum(item.total_price for item in self.cart_items.all())
        # total = 0
        # for item in self.cart_items.all():
        # total += item.total_price
        # return total

    def __str__(self):
        return f"cart of {self.user.email}: {self.id}"


# alright, I can add any product varient for any product.
# i need to accept cart items with the products that actually have the posted varients.
# or maybe list all the product varients of the product
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="products",
    )
    product_varient = models.ForeignKey(
        ProductVarient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    is_paid = models.BooleanField(default=False)

    # @property
    # def in_stock(self):
    #     stock_left = Product.objects.count()
    #     return stock_left >= 0

    @property
    def unit_price(self):
        if self.product_varient and self.product_varient.price:
            return self.product_varient.price
        return self.product.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    class Meta:
        unique_together = ["cart", "product", "product_varient"]
