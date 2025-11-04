from django.contrib import admin
from .models import Discount, Order, OrderItems


class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0
    readonly_fields = ["total_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "user__email"]
    readonly_fields = ["id", "total_amount", "created_at", "updated_at"]
    inlines = [OrderItemsInline]


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ["order", "item", "quantity", "total_price"]
    list_filter = ["order__status", "created_at"]
    readonly_fields = ["total_price", "created_at"]


admin.site.register(Discount)
