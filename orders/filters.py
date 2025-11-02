import django_filters
from .models import Order, OrderItems


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(field_name="status",choices=Order.STATUS_CHOICES)
    user_email = django_filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    order_id = django_filters.CharFilter(field_name="id", lookup_expr="icontains")
    user_first_name = django_filters.CharFilter(
        field_name="user__first_name", lookup_expr="icontains"
    )
    user_last_name = django_filters.CharFilter(
        field_name="user__last_name", lookup_expr="icontains"
    )
    user_email = django_filters.CharFilter(
        field_name="user__email", lookup_expr="icontains"
    )

    # Date filters
    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte"
    )
    created_date = django_filters.DateFilter(
        field_name="created_at__date",
    )
    #__year
    #__month
    #__day
    #__week
    #__week_day
    #__quarter
    #__hour
    #__minute
    #__second

    date_from = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="gte"
    )
    date_to = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="lte"
    )
    

    class Meta:
        model = Order
        fields = []

class OrderItemFilters(django_filters.FilterSet):

    class Meta:
        model = OrderItems
        fields = ["order", "item"]
