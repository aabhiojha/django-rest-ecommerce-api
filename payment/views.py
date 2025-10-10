from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
import stripe

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart, CartItem
from orders.models import Order, OrderItems
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentCreateSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(APIView):
    """
    create stripe checkout session for an order
    """

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

            # line items for Stripe
            line_items = []
            for item in order.order_items.all():
                line_items.append(
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(item.total_price * 100),
                            "product_data": {
                                "name": item.item.product.name,
                                "description": f"Quantity: {item.quantity}",
                            },
                        },
                        "quantity": item.quantity,
                    }
                )

            # make stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri("/payment/success/"),
                cancel_url=request.build_absolute_uri("/payment/cancel/"),
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

            # create or update Payment object
            payment, created = Payment.objects.update_or_create(
                order=order,
                defaults={
                    "user": request.user,
                    "amount": order.total_amount,
                    "status": "pending",
                    "stripe_payment_intent_id": checkout_session.get("payment_intent"),
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

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError as e:
        print(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    try:
        # payment_intent.created
        # bug was payment intent 
        if event["type"] == "payment_intent.created":
            payment_intent = event["data"]["object"]
            metadata = payment_intent.get("metadata", {})
            order_id = metadata.get("order_id")
            
            print(f"Payment intent created: {payment_intent['id']}, order: {order_id}")
            
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    payment = Payment.objects.get(order=order)
                    payment.stripe_payment_intent_id = payment_intent["id"]
                    payment.save()
                    
                    print(f"stripe_payment_intent_id inserted in the payment object: {payment_intent['id']}")
                except Order.DoesNotExist:
                    print(f"Order not found: {order_id}")
                except Payment.DoesNotExist:
                    print(f"Payment not found for order: {order_id}")
        

        # checkout.session.completed
        elif event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            metadata = session.get("metadata", {})
            order_id = metadata.get("order_id")

            print("in checkout.session.completed code")
            print("order_id","payment_intent_id")
            print(f"Checkout session completed: {session['id']}, order: {order_id}")

            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = "confirmed"
                    print(f"Order status updated to {order.status}")
                    order.save()

                    payment = Payment.objects.get(order=order)
                    payment.status = "completed"
                    print(f"payment status updated to {payment.status}")
                    payment.save()

                    # need to make cart item's is_paid flag True
                    order_items = order.order_items.all()
                    for order_item in order_items:
                        cart_item = order_item.item
                        cart_item.is_paid = True
                        cart_item.save()
                        print(f"Marked cart item {cart_item.id} as paid")

                except Order.DoesNotExist:
                    print(f"Order not found: {order_id}")

        # handles other events
        else:
            print(f"Unhandled event type: {event['type']}")

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        
    return HttpResponse(status=200)


class PaymentSuccessView(APIView):
    """Payment success callback"""

    def get(self, request):
        session_id = request.GET.get("session_id")
        return Response(
            {
                "status": "success",
                "message": "Payment completed successfully",
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
