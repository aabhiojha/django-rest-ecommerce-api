from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_varient_name = serializers.CharField(
        source="product_varient.name", read_only=True
    )
    unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_varient_name",
            "quantity",
            "unit_price",
            "total_price",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, attrs):
        product = attrs.get("product")
        product_varient = attrs.get("product_varient")

        if product_varient and product_varient.product != product:
            raise serializers.ValidationError(
                "Product varient must belong to the specified product"
            )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "cart_items",
            "item_count",
            "total",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
        }
