from rest_framework import serializers
from .models import Review


class ListReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "product",
            "user",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]

        # read_only_fields = [
        #     "product",
        #     "user",
        #     "rating",
        #     "comment",
        #     "created_at",
        #     "updated_at",
        # ]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "product",
            "rating",
            "comment",
        ]


class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]
