from django.db.models import F
from django.utils import timezone
from .models import Inventory, StockTransaction, InventoryBatch, Supplier, WasteRecord

# Class: InventoryRepository
class InventoryRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(inventory_id):
        return Inventory.objects.select_related('product', 'branch', 'business').get(id=inventory_id)

    @staticmethod
    # Method: get_by_product_and_branch
    def get_by_product_and_branch(product_id, branch_id):
        return Inventory.objects.filter(product_id=product_id, branch_id=branch_id).first()

    @staticmethod
    # Method: get_low_stock
    def get_low_stock(business_id):
        return Inventory.objects.filter(business_id=business_id, current_stock__lte=F('reorder_level'))

    @staticmethod
    # Method: update_stock_atomic
    def update_stock_atomic(inventory_id, quantity_change, field='current_stock'):
        """Atomically update a stock field using F expressions."""
        kwargs = {field: F(field) + quantity_change, 'last_stock_update': timezone.now()}
        Inventory.objects.filter(id=inventory_id).update(**kwargs)
        # Return updated instance
        return InventoryRepository.get_by_id(inventory_id)


# Class: StockTransactionRepository
class StockTransactionRepository:
    @staticmethod
    # Method: create_transaction
    def create_transaction(inventory_id, transaction_type, quantity, user_id, source_id=None, destination_id=None, remarks=None, reference_number=None):
        return StockTransaction.objects.create(
            inventory_id=inventory_id,
            transaction_type=transaction_type,
            quantity=quantity,
            created_by_id=user_id,
            source_id=source_id,
            destination_id=destination_id,
            remarks=remarks,
            reference_number=reference_number
        )


# Class: InventoryBatchRepository
class InventoryBatchRepository:
    @staticmethod
    # Method: get_active_batches_fifo
    def get_active_batches_fifo(inventory_id):
        return InventoryBatch.objects.filter(
            inventory_id=inventory_id,
            status=InventoryBatch.BatchStatus.ACTIVE,
            quantity__gt=0
        ).order_by('received_date', 'created_at')

    @staticmethod
    # Method: get_expiring_soon
    def get_expiring_soon(days=30):
        target_date = timezone.now().date() + timezone.timedelta(days=days)
        return InventoryBatch.objects.filter(
            status=InventoryBatch.BatchStatus.ACTIVE,
            expiry_date__lte=target_date,
            expiry_date__gt=timezone.now().date()
        )
        
    @staticmethod
    # Method: update_batch_quantity
    def update_batch_quantity(batch_id, quantity_change):
        InventoryBatch.objects.filter(id=batch_id).update(quantity=F('quantity') + quantity_change)
        batch = InventoryBatch.objects.get(id=batch_id)
        if batch.quantity <= 0:
            batch.status = InventoryBatch.BatchStatus.DEPLETED
            batch.save(update_fields=['status'])
        return batch


# Class: SupplierRepository
class SupplierRepository:
    @staticmethod
    # Method: get_active_suppliers
    def get_active_suppliers(business_id):
        return Supplier.objects.filter(business_id=business_id, is_active=True)


# Class: WasteRecordRepository
class WasteRecordRepository:
    @staticmethod
    # Method: create_waste_record
    def create_waste_record(inventory_id, quantity, reason, user_id, remarks=None, image=None):
        return WasteRecord.objects.create(
            inventory_id=inventory_id,
            quantity=quantity,
            waste_reason=reason,
            recorded_by_id=user_id,
            remarks=remarks,
            image=image
        )
