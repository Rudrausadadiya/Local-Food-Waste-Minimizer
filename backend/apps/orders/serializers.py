from rest_framework import serializers
from django.db import transaction
from .models import Customer, Order, OrderItem, Payment, Invoice, Sale, LoyaltyTransaction, Delivery
from .services import OrderService

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_deleted')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'tax_rate', 'discount', 'total_price']
        read_only_fields = ('id', 'total_price')

class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class OrderWriteSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'business', 'branch', 'customer', 'reservation_id', 
            'order_number', 'order_type', 'notes', 'created_by', 'delivery_charge', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # OrderService handles the calculation, stock reservation, and creation atomically
        order = OrderService.create_order(order_data=validated_data, items_data=items_data)
        return order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'
