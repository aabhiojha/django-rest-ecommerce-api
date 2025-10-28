from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductUpdateSerializer,
    CategoryProductListSerializer
)

from .models import Category, ProductVarient, ProductImage, Product

from .pagination import ProductCursorPagination
from .filters import ProductFilter


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    lookup_field = "pk"
    serializer_class = CategoryDetailSerializer


class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer


# Product
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductListSerializer
    pagination_class = ProductCursorPagination
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "brand", "description", "sku"]


class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer


class ProductUpdateAPIView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    lookup_field = "pk"
    serializer_class = ProductUpdateSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category").prefetch_related(
        "images", "varients"
    )
    # queryset = Product.objects.all()
    lookup_field = "pk"
    serializer_class = ProductDetailSerializer


class ProductFeaturedAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_featured=True)
    serializer_class = ProductListSerializer
    pagination_class = ProductCursorPagination


class CategoryProductAPIView(APIView):
    """Gets all the products in that category"""
    serializer_class = CategoryProductListSerializer

    def get(self, request, pk):
        category_id = self.kwargs.get("pk")
        queryset = Product.objects.filter(category_id=category_id).order_by("-created_at")
        serializer =  CategoryProductListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    