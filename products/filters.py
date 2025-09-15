import django_filters
from django_filters.rest_framework import FilterSet
from .models import Product


class ProductFilter(FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category__id")
    category_name = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    is_featured = django_filters.BooleanFilter()
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = [
            "brand",
            "category",
            "is_featured",
            "name",
        ]
