from rest_framework import serializers
from orders.models import Order
from payment.models import Payment, StripePaymentIntent


class PaymentSerializer(serializers.ModelSerializer):
    """Basic payment serializer for CRUD operations"""
    
    buyer_name = serializers.CharField(source="order.user.get_full_name", read_only=True)
    order_total = serializers.DecimalField(source="order.total_amount", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "buyer_name",
            "order_total",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "stripe_payment_intent_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "buyer_name",
            "order_total",
            "status",
            "transaction_id",
            "stripe_payment_intent_id",
            "created_at",
            "updated_at",
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a payment"""

    class Meta:
        model = Payment
        fields = ["order", "payment_method"]

    def validate_order(self, value):
        """Validate order belongs to current user"""
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only create payments for your own orders.")
        
        if value.status != "pending":
            raise serializers.ValidationError("Payment can only be created for pending orders.")
        
        return value


class StripePaymentIntentSerializer(serializers.ModelSerializer):
    """Serializer for Stripe payment intent"""

    class Meta:
        model = StripePaymentIntent
        fields = [
            "id",
            "payment",
            "stripe_payment_intent_id",
            "client_secret",
            "amount",
            "currency",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "stripe_payment_intent_id",
            "client_secret",
            "created_at",
            "updated_at",
        ]


class PaymentIntentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a Stripe payment intent"""
    
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ["order_id", "payment_method"]

    def validate_order_id(self, value):
        """Validate order exists and belongs to user"""
        request = self.context.get("request")
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        if request and order.user != request.user:
            raise serializers.ValidationError("You can only create payment for your own orders.")
        
        if order.status != "pending":
            raise serializers.ValidationError("Payment can only be created for pending orders.")
        
        return value

    def create(self, validated_data):
        """Create payment with order from order_id"""
        order_id = validated_data.pop("order_id")
        order = Order.objects.get(id=order_id)
        validated_data["order"] = order
        validated_data["amount"] = order.total_amount
        return super().create(validated_data)


class PaymentConfirmSerializer(serializers.ModelSerializer):
    """Serializer for confirming a payment"""
    
    payment_intent_id = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = Payment
        fields = ["payment_intent_id"]

    def update(self, instance, validated_data):
        """Update payment status after confirmation"""
        instance.stripe_payment_intent_id = validated_data.get("payment_intent_id")
        instance.status = "completed"
        instance.save()
        return instance