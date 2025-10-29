from rest_framework import serializers

from products.models import Product, ProductVarient
from .models import Cart, CartItem, Favourite


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
        print(attrs)

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


class AddItemSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_varient = serializers.PrimaryKeyRelatedField(
        queryset=ProductVarient.objects.all(),
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_varient",
            "quantity",
        ]

    def create(self, validated_data):
        print(validated_data)
        user = self.context["request"].user
#         Sample Django request object attributes and example values:
            # request.method: HTTP method like "GET" or "POST"
            # request.path: URL path requested, e.g. "/example/path/"
            # request.GET: Query parameters dictionary-like object, e.g. {"name": "John"}
            # request.POST: POST form data dictionary-like object (if POST request)
            # request.headers: Dictionary-like object with HTTP headers
            # request.user: The currently authenticated user (or AnonymousUser)
            # request.session: Session data dictionary-like object
            # request.is_secure(): Boolean, True if request uses HTTPS
            # request.FILES: Uploaded files dictionary (if any)
        # print(self.context['request'].method)
        product = self.validated_data["product"]
        product_varient = self.validated_data["product_varient"]
        quantity = self.validated_data["quantity"]
        # suru ma ta cart chaiyooo of that user
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            print("Cart is created")
        # check if cartitem already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_varient=product_varient,
            quantity=quantity,
        )
        return cart_item


class UpdateCartItemQuantitySerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        # takes only quantity
        fields = [
            "id",
            "product",
            "product_varient",
            "quantity",
            ]
        read_only_fields = [
            "id",
            "product",
            "product_varient",
        ]

    # def validate(self, attrs):
    #     print(attrs)

# favourite
class ListFavouriteSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Favourite
        fields = ["id", "product", "product_name"]


class CreateFavouriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = ["product"]

    def create(self, validated_data):
        try:
            user = self.context["request"].user
            favourite = Favourite.objects.create(user=user, **validated_data)
            return favourite
        except Exception as e:
            raise serializers.ValidationError({"error": "Could not add to favorites."})


class RemoveFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = []
