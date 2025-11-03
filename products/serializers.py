from rest_framework import serializers

from cart.models import CartItem
from orders.models import OrderItems
from orders.serializers import OrderItemSerializer
from reviews.serializers import ListReviewSerializer
from .models import Category, Product, ProductImage, ProductVarient
from django.utils.text import slugify
from core.utils.custom_slugify import slugify_name

# Category serializers


class CategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "sort_order",
            "parent",
            "children",
        ]

    def get_children(self, obj):
        if obj.children.exists():
            return CategoryListSerializer(obj.children.all(), many=True).data
        return []


class CategoryCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=True, allow_blank=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "sort_order",
            "parent",
        ]

    def create(self, validated_data):
        if not validated_data.get("slug"):
            base_slug = slugify(validated_data["name"])
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            validated_data["slug"] = slug
        return super().create(validated_data)


class CategoryDetailSerializer(serializers.ModelSerializer):
    children = CategoryListSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "sort_order",
            "parent",
            "parent_name",
            "children",
            "created_at",
            "updated_at",
        ]


# Product Varient
class ProductVarientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVarient
        fields = ["id", "name", "sku", "price"]


# Product Image
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "alt_text", "is_primary", "sort_order"]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "description",
            "long_description",
            "price",
            "sku",
            "quantity",
            "brand",
            "primary_image",
            "stock_status",
            "weight",
            "dimensions",
            "is_featured",
            "is_digital",
            "average_rating",
            "review_count",
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class CategoryProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "long_description",
            "price",
            "sku",
            "brand",
            "primary_image",
            "weight",
            "dimensions",
            "is_featured",
            "is_digital",
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    varients = ProductVarientSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    # reviews = ListReviewSerializer(many=True, read_only=True)
    reviews = ListReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "category",
            "varients",
            "images",
            "additional_info",
            "description",
            "long_description",
            "price",
            "sku",
            "brand",
            "weight",
            "dimensions",
            "is_featured",
            "is_digital",
            "created_at",
            "updated_at",
            "reviews",
            "average_rating",
            "review_count",
        ]

    # def get_reviews(self, )


class ProductCreateSerializer(serializers.ModelSerializer):
    varients = ProductVarientSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "category",
            # "images",
            # "attributes",
            "additional_info",
            "description",
            "long_description",
            "price",
            "sku",
            "brand",
            "weight",
            "dimensions",
            "varients",
            "is_featured",
            "is_digital",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        varient_values = validated_data.pop("varients")
        product = Product.objects.create(**validated_data)
        if varient_values:
            for varient in varient_values:
                created = ProductVarient.objects.create(product=product, **varient)
                print(created)
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    varients = ProductVarientSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "category",
            "additional_info",
            "description",
            "long_description",
            "price",
            "sku",
            "brand",
            "weight",
            "dimensions",
            "varients",
            "is_featured",
            "is_digital",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        # check if the item is in anyone's cart
        # print(instance.id)
        cart_items = CartItem.objects.all()
        for item in cart_items:
            if instance.id == item.product.id:
                raise serializers.ValidationError(
                    "The product is already in cart and it cannot be updated now."
                )

        print(cart_items)
        variant_data = validated_data.pop("varients", None)

        # updating values in the product instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if "name" in validated_data and "slug" not in validated_data:
            instance.slug = slugify_name(Product, validated_data)

            instance.save()

            if variant_data is not None:
                instance.varients.all().delete()
                if variant_data:
                    ProductVarient.objects.bulk_create(
                        [
                            ProductVarient(product=instance, **item)
                            for item in variant_data
                        ]
                    )
        return instance


class SellerProductOrdersSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="item.product")
    sku = serializers.CharField(source="item.product.sku")
    category = serializers.CharField(source="item.product.category")
    description = serializers.CharField(source="item.product.description")
    unit_price = serializers.FloatField(source="item.unit_price")
    variant = serializers.CharField(source="item.product_varient")
    brand =  serializers.CharField(source="item.product.brand")
    # total_price = serializers.SerializerMethodField()
    order_status = serializers.CharField(source="order.status")

    class Meta:
        model = OrderItems
        fields = [
            "order",
            "sku",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
            "variant",
            "description",
            "brand",
            "category",
            "order_status",
            "created_at",
        ]
        read_only_fields = fields
