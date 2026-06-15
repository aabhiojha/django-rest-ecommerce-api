from django.urls import path
from . import views

urlpatterns=[
    path("list/<int:pk>", views.ListReviewsView.as_view()),
    path("create", views.CreateReviewView.as_view()),
    path("edit/<int:pk>", views.UpdateReviewView.as_view()),
    path("delete/<int:pk>", views.DeleteReviewView.as_view()),
    path("reply/<int:pk>", views.ReplyToReviewView.as_view()),
]