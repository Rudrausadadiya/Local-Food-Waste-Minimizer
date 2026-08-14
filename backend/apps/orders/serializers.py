from rest_framework import serializers
from .models import Customer, Order, OrderItem, Payment, Invoice, Sale, LoyaltyTransaction, Delivery
from .services import OrderService

# Class: CustomerSerializer
class CustomerSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_deleted')

# Class: OrderItemSerializer
class OrderItemSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'tax_rate', 'discount', 'total_price']
        read_only_fields = ('id', 'total_price')

# Class: DeliverySerializer
class DeliverySerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Delivery
        fields = '__all__'

# Class: OrderReadSerializer
class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery = DeliverySerializer(read_only=True)
    
    # Class: Meta
    class Meta:
        model = Order
        fields = '__all__'

# Class: OrderWriteSerializer
class OrderWriteSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    redeem_points = serializers.IntegerField(required=False, default=0, write_only=True)
    delivery_address = serializers.CharField(required=False, default='', write_only=True)
    
    # Class: Meta
    class Meta:
        model = Order
        fields = [
            'business', 'branch', 'customer', 'reservation_id', 
            'order_number', 'order_type', 'notes', 'created_by', 'delivery_charge', 'items',
            'redeem_points', 'delivery_address'
        ]

    # Method: create
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        return OrderService.create_order(order_data=validated_data, items_data=items_data)

# Class: PaymentSerializer
class PaymentSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

# Class: InvoiceSerializer
class InvoiceSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Invoice
        fields = '__all__'

# Class: SaleSerializer
class SaleSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Sale
        fields = '__all__'

# Class: LoyaltyTransactionSerializer
class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = LoyaltyTransaction
        fields = '__all__'

# Class: DeliverySerializer
class DeliverySerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Delivery
        fields = '__all__'
