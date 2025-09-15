import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category__id")
    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = []
