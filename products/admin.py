from django.contrib import admin
from .models import Product, Category, ProductImage, ProductVarient

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVarient)
# admin.site.register(ProductAttribute)
admin.site.register(ProductImage)
