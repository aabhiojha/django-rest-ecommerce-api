from rest_framework import serializers
from .models import Reply, Review


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

    # def get_reply(self, review):
    #     replies = review.replies.all()
    #     print(replies)
    #     return replies



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
