from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from reviews.models import Review
from .serializers import ReviewSerializer


class ListReviews(APIView):
    serializer_class = ReviewSerializer

    def get(self, request):
        queryset = Review.objects.all()
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
