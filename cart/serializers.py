from rest_framework import serializers

from products.models import Product, ProductVarient
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

    def create(self, validated_data):
        return super().create(validated_data)


# class AddItemSerializer(serializers.Serializer):
#     product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
#     product_varient = serializers.PrimaryKeyRelatedField(
#         queryset=ProductVarient.objects.all(),
#     )
#     quantity = serializers.IntegerField(min_value=1, default=1)

#     def validate(self, attrs):
#         product = attrs.get("product")
#         product_varient = attrs.get("product_varient")
#         if product_varient and product_varient.product != product:
#             raise serializers.ValidationError(
#                 "Product varient must belong to the specified product"
#             )
#         return attrs

#     def create(self, validated_data):
#         user = self.context["request"].user
#         product = validated_data["product"]
#         product_varient = validated_data["product_varient"]
#         quantity = validated_data["quantity"]

#         cart, created = Cart.objects.get_or_create(user=user)

#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=product,
#             product_varient=product_varient,
#             quantity=quantity,
#         )

#         cart_item.save()
#         return cart_item


class AddItemSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_varient = serializers.PrimaryKeyRelatedField(
        queryset=ProductVarient.objects.all(),
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    class Meta:
        model = CartItem
        fields = ["product", "product_varient", "quantity"]


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    def validate(self, attrs):
        if attrs["quantity"] <= 0:
            raise serializers.ValidationError("The quantity must be postive number")
        return attrs
