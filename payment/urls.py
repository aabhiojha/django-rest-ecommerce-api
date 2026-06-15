from django.urls import path
from . import views

urlpatterns = [
    # Stripe webhook
    path("webhook", views.stripe_webhook, name="stripe-webhook"),
    path("list", views.PaymentListView.as_view(), name="payment-list"),
    
    # Success and cancel callbacks
    path("success", views.PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel", views.PaymentCancelView.as_view(), name="payment-cancel"),
]