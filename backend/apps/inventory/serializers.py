from rest_framework import serializers
from .models import Inventory, StockTransaction, InventoryBatch, WasteRecord, Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    available_stock = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ['current_stock', 'damaged_stock', 'expired_stock', 'reserved_stock', 'average_cost', 'last_stock_update']


class StockTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class InventoryBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryBatch
        fields = '__all__'


class WasteRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteRecord
        fields = '__all__'
        read_only_fields = ['recorded_by', 'created_at']


# Action specific serializers
class StockInSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    reference_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_null=True)
    batch_number = serializers.CharField(max_length=100, required=True)
    manufacturing_date = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    purchase_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    supplier = serializers.UUIDField(required=False, allow_null=True)
    supplier_invoice_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    storage_location = serializers.CharField(max_length=100, required=False, allow_null=True)


class StockOutSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    reference_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_null=True)


class StockTransferSerializer(serializers.Serializer):
    inventory_to_id = serializers.UUIDField(required=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    reference_number = serializers.CharField(max_length=100, required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_null=True)


class RecordWasteSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    reason = serializers.ChoiceField(choices=WasteRecord.WasteReason.choices, required=True)
    remarks = serializers.CharField(required=False, allow_null=True)
    image = serializers.URLField(required=False, allow_null=True)
