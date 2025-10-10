from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
import stripe

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentCreateSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(APIView):
    """Create Stripe checkout session for an order"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Validate input
        serializer = PaymentCreateSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_id = serializer.validated_data["order_id"]
            order = Order.objects.get(id=order_id, user=request.user)

            # Build line items for Stripe
            line_items = []
            for item in order.order_items.all():
                line_items.append(
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(item.total_price * 100),  # Convert to cents
                            "product_data": {
                                "name": item.item.product.name,
                                "description": f"Quantity: {item.quantity}",
                            },
                        },
                        "quantity": item.quantity,
                    }
                )

            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri("/api/payment/success/")
                + f"?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=request.build_absolute_uri("/api/payment/cancel/"),
                metadata={
                    "order_id": str(order.id),
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order.id),
                        "user_id": str(request.user.id),
                        "user_email": str(request.user.email),
                    }
                },
            )

            # Create or update Payment object
            payment, created = Payment.objects.update_or_create(
                order=order,
                defaults={
                    "user": request.user,
                    "amount": order.total_amount,
                    "status": "pending",
                    "stripe_payment_intent_id": checkout_session.payment_intent,
                },
            )

            return Response(
                {
                    "session_id": checkout_session.id,
                    "checkout_url": checkout_session.url,
                    "payment_id": payment.id,
                }
            )

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error in PaymentView: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    try:
        # Handle checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_id = session.get("metadata", {}).get("order_id")

            if order_id:
                order = Order.objects.get(id=order_id)
                payment = Payment.objects.get(order=order)

                payment.status = "processing"
                if session.payment_intent:
                    payment.stripe_payment_intent_id = session.payment_intent
                payment.save()

                order.status = "processing"
                order.save()

        # Handle payment_intent.succeeded event
        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]

            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent.id
                )
                payment.status = "completed"
                payment.save()

                order = payment.order
                order.status = "completed"
                order.save()
            except Payment.DoesNotExist:
                pass

        # Handle payment_intent.payment_failed event
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]

            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent.id
                )
                payment.status = "failed"
                payment.save()

                order = payment.order
                order.status = "failed"
                order.save()
            except Payment.DoesNotExist:
                pass

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return HttpResponse(status=500)

    return HttpResponse(status=200)


class PaymentSuccessView(APIView):
    """Payment success callback"""

    def get(self, request):
        session_id = request.GET.get("session_id")
        return Response(
            {
                "status": "success",
                "message": "Payment completed successfully",
                "session_id": session_id,
            }
        )


class PaymentCancelView(APIView):
    """Payment cancel callback"""

    def get(self, request):
        return Response({"status": "cancelled", "message": "Payment was cancelled"})


class PaymentListView(APIView):
    """List user's payments"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
