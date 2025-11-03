from rest_framework import serializers
from .models import Reply, Review
from cart.models import Cart, CartItem

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"


class ListReviewSerializer(serializers.ModelSerializer):
    # reply = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "comment",
            "created_at",
            "updated_at",
            "replies"
        ]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "product",
            "rating",
            "comment",
        ]

    # need to check if the product is already bought by the user
    # before leaving a review about it.
    def validate(self, attrs):
        user = self.context.get("request").user
        print(attrs)
        product = attrs.get("product")
        print(product.id)
        # get the cartitem object with that product and user
        cart_item = CartItem.objects.filter(product=product, is_paid=True, cart__user=user)
        if not cart_item:
            raise serializers.ValidationError("The product does not exist or is not paid to leave review.")
        return super().validate(attrs)

class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]
    

class ReplyToReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = [
            "message"
        ]
        read_only_fields = [
            'id',
            'seller',
            "reviewer",
        ]
