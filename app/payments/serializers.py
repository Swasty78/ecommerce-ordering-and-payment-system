from rest_framework import serializers
from .models import Payment
from orders.models import Order
from core.constants import PaymentProvider

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'order', 'amount', 'provider', 'transaction_id', 'status', 'created_at']
        read_only_fields = ['user', 'amount', 'status', 'created_at', 'transaction_id']

    def validate_provider(self, value):
        if value not in PaymentProvider.values:
            raise serializers.ValidationError("Invalid payment provider.")
        return value

    def create(self, validated_data):
        order = validated_data['order']
        # Ensure the user creating the payment owns the order
        request = self.context.get('request')
        if request and request.user != order.user:
            raise serializers.ValidationError("You can only make payments for your own orders.")
            
        validated_data['user'] = request.user
        validated_data['amount'] = order.total_amount
        return super().create(validated_data)
