from django.db import models
from core.models import BaseModel
from products.model_validators import validate_price
from users.models import User


class Category(BaseModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        stripped_name = self.name.lower().split(" ")
        self.slug = "-".join(stripped_name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Category {self.id}: {self.name}"

    class Meta:
        verbose_name_plural = "Categories"


class Product(BaseModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    # To track which user added the product
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="products")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    description = models.TextField(default="", help_text="Short Description")
    long_description = models.TextField(
        blank=True, default="", help_text="Long Description"
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[validate_price]
    )
    # stock keeping unit (nike shoes 11 red -> nike-sho-11-r)
    sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(blank=True, default="")
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    dimensions = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    additional_info = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        stripped_name = self.name.lower().split(" ")
        self.slug = "-".join(stripped_name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}: {self.name} and {self.sku}"


class ProductVarient(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="varients"
    )
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00, blank=True
    )

    def __str__(self):
        return f"{self.id}: {self.product.name}'s {self.sku}"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField()
    sort_order = models.IntegerField(default=0)
