from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from orders.models import Order, OrderItems
from cart.models import CartItem


class OrderSerializer(serializers.ModelSerializer):
    order_items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "status", "order_items_count", "total_amount"]
        read_only_fields = ["id"]

    def get_order_items_count(self, obj):
        return obj.order_items.count()

    def get_total_amount(self, obj):
        total = 0
        for item in obj.order_items.all():
            total += item.item.product.price * item.quantity
        return total


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="item.product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="item.product.price", read_only=True, max_digits=10, decimal_places=2
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = [
            "id",
            "item",
            "quantity",
            "product_name",
            "product_price",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.item.product.price * obj.quantity


class OrderItemsCreateSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    list_of_items = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of CartItem IDs to add to the order",
    )

    class Meta:
        model = OrderItems
        fields = ["order", "list_of_items"]

    def validate_list_of_items(self, value):
        if not value:
            raise ValidationError("List of items cannot be empty")

        existing_items = CartItem.objects.filter(id__in=value)
        existing_ids = set(existing_items.values_list("id", flat=True))
        missing_ids = set(value) - existing_ids

        if missing_ids:
            raise ValidationError(f"Cart items with IDs {missing_ids} do not exist")

        already_purchased = existing_items.filter(purchased=True)
        if already_purchased.exists():
            purchased_ids = list(already_purchased.values_list("id", flat=True))
            raise ValidationError(
                f"Cart items with IDs {purchased_ids} are already purchased"
            )
        return value

    def create(self, validated_data):
        order = validated_data["order"]
        cart_item_ids = validated_data.pop("list_of_items")

        cart_items = CartItem.objects.filter(id__in=cart_item_ids)
        order_items = []

        for cart_item in cart_items:
            order_item = OrderItems.objects.create(
                order=order,
                item=cart_item,
                quantity=cart_item.quantity,
            )
            order_items.append(order_item)

            # update the cart_item purchased as True to remove it from displaying it in cart
            # thats in frontend tho
            cart_item.purchased = True
            cart_item.save()

        return {
            "order": order,
            "order_items": order_items,
            "count": len(order_items),
        }

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {
                "order_id": instance["order"].id,
                "order_items_count": instance["count"],
                "order_items": [
                    {
                        "id": item.id,
                        "product_name": item.item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.item.product.price),
                        "total_price": float(item.item.product.price * item.quantity),
                    }
                    for item in instance["order_items"]
                ],
                "total_amount": sum(
                    float(item.item.product.price * item.quantity)
                    for item in instance["order_items"]
                ),
            }
        return super().to_representation(instance)
