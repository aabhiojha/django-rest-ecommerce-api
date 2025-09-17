from rest_framework import serializers
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


# # product attribute
# class ProductAttributeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductAttribute
#         fields = ["id", "name", "value"]


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
    # category = CategoryListSerializer(read_only=True)
    varients = ProductVarientSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    # attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "category",
            "varients",
            "images",
            # "attributes",
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
        ]


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
        varient_data = validated_data.pop("varients")
        validated_data = slugify_name(Product, validated_data=validated_data)
        product = Product.objects.update(**validated_data)
        # sku =
        for varient in varient_data:
            ProductVarient.objects.update(product=product, **varient)
        return product
