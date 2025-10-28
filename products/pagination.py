from rest_framework.pagination import CursorPagination


class ProductCursorPagination(CursorPagination):
    page_size = 20
    ordering = ["-created_at"]

class ProductFeaturedCursorPagination(CursorPagination):
    page_size = 3
    