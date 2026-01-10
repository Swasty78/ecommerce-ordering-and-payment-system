from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')
        read_only_fields = ('id', 'price', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'order_items', 'shipping_address', 'total_amount', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'total_amount', 'status', 'created_at')

    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        user = self.context['request'].user
        
        with transaction.atomic():
            # 1. Create Order
            order = Order.objects.create(user=user, **validated_data)
            
            total_amount = 0
            
            # 2. Create Order Items
            for item_data in items_data:
                product_id = item_data['product_id']
                quantity = item_data['quantity']
                
                # Fetch product to get current price
                product = Product.objects.get(id=product_id)
                
                # Check stock (Optional but good practice)
                if product.stock < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")
                
                price = product.price
                subtotal = price * quantity
                total_amount += subtotal
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                # Reduce stock
                product.stock -= quantity
                product.save()
                
            # 3. Update Order Total
            order.total_amount = total_amount
            order.save()
        
        return order
