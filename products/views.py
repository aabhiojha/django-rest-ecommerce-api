from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasPermissions
from users.models import User

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
)

from .models import Category, ProductVarient, ProductImage, Product

from .pagination import ProductCursorPagination
from .filters import ProductFilter


# class CategoryListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategoryListSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_manage_all_products"]


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    lookup_field = "pk"
    serializer_class = CategoryDetailSerializer


# Product
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductListSerializer
    pagination_class = ProductCursorPagination
    filterset_class = ProductFilter
    search_fields = ["name", "brand", "description", "sku"]


class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_create_products"]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductUpdateAPIView(APIView):
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_edit_own_products"]

    def patch(self, request, pk):
        product_instance = Product.objects.get(id=pk, user=self.request.user)
        serializer = ProductUpdateSerializer(product_instance,data=request.data, context={"product_id":pk}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related("reviews", "images", "varients")
    lookup_field = "pk"
    serializer_class = ProductDetailSerializer


class ProductDeleteAPIView(generics.DestroyAPIView):
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_delete_own_products"]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

class SellerProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, HasPermissions]
    permissions_required = ["can_view_own_products"]

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.filter(user=user)
        return queryset
    
