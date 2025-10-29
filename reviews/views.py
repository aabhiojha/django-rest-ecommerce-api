from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from reviews.models import Review
from .serializers import CreateReviewSerializer, ListReviewSerializer,UpdateReviewSerializer

from core.permissions import HasPermissions
from rest_framework.permissions import IsAuthenticated

class ListReviewsView(APIView):
    serializer_class = ListReviewSerializer
    # viewing reviews doesn't require authentication

    def get(self, request):
        queryset = Review.objects.all()
        serializer = ListReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CreateReviewView(APIView):
    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_create_review"

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateReviewView(APIView):
    serializer_class = UpdateReviewSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_edit_own_review"

    # need to check if the review is made by request.user

    def patch(self, request, pk):
        review = Review.objects.get(id=pk)
        if review.user != request.user:
            return Response({"error":"You cannot make changes to other's reviews"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteReviewView(APIView):
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = "can_delete_own_review"

    def delete(self, request, pk):
        review = get_object_or_404(Review, id=pk)
        if review.user != request.user:
            return Response({"error":"You cannot make changes to other's reviews"}, status=status.HTTP_400_BAD_REQUEST)

        if review:
            review.delete()
        return Response({"message":f"User {request.user} is successfully deleted."}, status=status.HTTP_200_OK)
