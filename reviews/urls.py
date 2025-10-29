from django.urls import path
from . import views

urlpatterns=[
    path("list/", views.ListReviews.as_view())
]