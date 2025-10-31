from rest_framework import serializers
from payment.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    order_id = serializers.CharField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "order_id",
            "order",
            "amount",
            "status",
            "stripe_payment_intent_id",
            "created_at",
            "updated_at",
        ]
    
        read_only_fields = [
            "id",
            'user',
            "user_email",
            "user_name",
            "order_id",
            "status",
            "stripe_payment_intent_id",
            "created_at",
            "updated_at",
        ]


from orders.models import Order
class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payment"""

    order_id = serializers.CharField()

    def validate_order_id(self, value):
        request = self.context.get("request")

        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        if request and order.user != request.user:
            raise serializers.ValidationError("You can only create payments for your own orders.")
        
        if order.status == 'completed':
            raise serializers.ValidationError("Order is already paid.")
        
        if not order.order_items.exists():
            raise serializers.ValidationError("Order has no items.")
        
        return value