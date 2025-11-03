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
            "is_paid"
        ]


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
        required=False
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

        if quantity >= product.quantity:
            raise serializers.ValidationError("Quantity cannot be greater than the product stock.")
        
        # user can pass product varient or not
        if product_varient is not None:
            # bug
            # user should not be able to add any product varient of any product 
            product_obj = Product.objects.get(id=product.id)
            product_varient_list = []
            product_varient_queryset = product_obj.varients.filter(product=product_obj)
            print(product_varient_queryset)
            for varient in product_varient_queryset:
                product_varient_list.append(varient.id)
            print(product_varient_list)
            print(self.validated_data["product_varient"].id)
            if self.validated_data["product_varient"].id not in product_varient_list:
                raise serializers.ValidationError("Not valid product Varient choice for the product")

        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            print("Cart is created")
        # check if cartitem already exists
        if product_varient:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                product_varient=product_varient,
                quantity=quantity,
            )
        else:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                product_varient="Default Product",
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
