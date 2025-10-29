import django_filters
from .models import Product
from django.db.models import Q


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    category_name = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    is_featured = django_filters.BooleanFilter()
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    # django_filters.ModelMultipleChoiceFilter

    class Meta:
        model = Product
        fields = [
            "brand",
            "category",
            "is_featured",
            "name",
        ]
