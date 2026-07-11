from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import StockTransaction, InventoryBatch, WasteRecord
from .repositories import InventoryRepository, StockTransactionRepository, InventoryBatchRepository, WasteRecordRepository
from .validators import validate_transfer_businesses, validate_stock_availability, validate_unique_batch
from .signals import stock_updated, batch_expired, waste_recorded, low_stock

class InventoryService:
    @staticmethod
    @transaction.atomic
    def stock_in(inventory_id: str, quantity: Decimal, user_id: str, batch_details: dict, reference_number: str = None, remarks: str = None):
        validate_unique_batch(inventory_id, batch_details['batch_number'])

        # Update Stock
        inventory = InventoryRepository.update_stock_atomic(inventory_id, quantity, field='current_stock')

        # Create Batch
        InventoryBatch.objects.create(
            inventory=inventory,
            quantity=quantity,
            **batch_details
        )

        # Create Transaction
        transaction_record = StockTransactionRepository.create_transaction(
            inventory_id=inventory_id,
            transaction_type=StockTransaction.TransactionType.STOCK_IN,
            quantity=quantity,
            user_id=user_id,
            destination_id=inventory.branch_id,
            reference_number=reference_number,
            remarks=remarks
        )

        # Emit Signal
        stock_updated.send(sender=InventoryService, inventory=inventory, transaction=transaction_record, quantity_change=quantity)
        
        return inventory

    @staticmethod
    @transaction.atomic
    def stock_out(inventory_id: str, quantity: Decimal, user_id: str, reference_number: str = None, remarks: str = None, source_id: str = None):
        inventory = InventoryRepository.get_by_id(inventory_id)
        validate_stock_availability(inventory, quantity)

        # Deduct from FIFO batches
        remaining_qty = quantity
        batches = InventoryBatchRepository.get_active_batches_fifo(inventory_id)
        
        for batch in batches:
            if remaining_qty <= Decimal('0.00'):
                break
            
            deduct_qty = min(batch.quantity, remaining_qty)
            InventoryBatchRepository.update_batch_quantity(batch.id, -deduct_qty)
            remaining_qty -= deduct_qty

        # Update Stock
        inventory = InventoryRepository.update_stock_atomic(inventory_id, -quantity, field='current_stock')

        # Create Transaction
        transaction_record = StockTransactionRepository.create_transaction(
            inventory_id=inventory_id,
            transaction_type=StockTransaction.TransactionType.STOCK_OUT,
            quantity=quantity,
            user_id=user_id,
            source_id=source_id or inventory.branch_id,
            reference_number=reference_number,
            remarks=remarks
        )

        # Emit Signal
        stock_updated.send(sender=InventoryService, inventory=inventory, transaction=transaction_record, quantity_change=-quantity)
        
        if inventory.current_stock <= inventory.reorder_level:
            low_stock.send(sender=InventoryService, inventory=inventory)
            
        return inventory

    @staticmethod
    @transaction.atomic
    def stock_transfer(inventory_from_id: str, inventory_to_id: str, quantity: Decimal, user_id: str, batch_details: dict = None, reference_number: str = None, remarks: str = None):
        inventory_from = InventoryRepository.get_by_id(inventory_from_id)
        inventory_to = InventoryRepository.get_by_id(inventory_to_id)
        
        validate_transfer_businesses(inventory_from, inventory_to)

        # Process Stock Out
        InventoryService.stock_out(
            inventory_id=inventory_from_id, 
            quantity=quantity, 
            user_id=user_id, 
            reference_number=reference_number, 
            remarks=remarks,
            source_id=inventory_from.branch_id
        )

        # For transfer IN, we create a new batch or add to existing if same batch info provided
        # In a real system, the exact batches deducted from source should ideally be transferred.
        # Here we simplify by treating the transfer as a new stock in with provided batch details.
        
        # Process Stock In
        if not batch_details:
            batch_details = {
                'batch_number': f"TRF-{reference_number or timezone.now().strftime('%Y%m%d%H%M%S')}",
            }
            
        InventoryService.stock_in(
            inventory_id=inventory_to_id,
            quantity=quantity,
            user_id=user_id,
            batch_details=batch_details,
            reference_number=reference_number,
            remarks=remarks
        )
        
        # Transaction record specifically for TRANSFER type
        StockTransactionRepository.create_transaction(
            inventory_id=inventory_from_id,
            transaction_type=StockTransaction.TransactionType.TRANSFER,
            quantity=quantity,
            user_id=user_id,
            source_id=inventory_from.branch_id,
            destination_id=inventory_to.branch_id,
            reference_number=reference_number,
            remarks=remarks
        )

    @staticmethod
    @transaction.atomic
    def record_waste(inventory_id: str, quantity: Decimal, reason: str, user_id: str, image: str = None, remarks: str = None):
        inventory = InventoryRepository.get_by_id(inventory_id)
        validate_stock_availability(inventory, quantity)

        # Update specific waste/damage stock piles based on reason
        if reason == WasteRecord.WasteReason.EXPIRED:
            inventory = InventoryRepository.update_stock_atomic(inventory_id, quantity, field='expired_stock')
        elif reason == WasteRecord.WasteReason.DAMAGED:
            inventory = InventoryRepository.update_stock_atomic(inventory_id, quantity, field='damaged_stock')
        
        # Deduct from total current stock
        inventory = InventoryRepository.update_stock_atomic(inventory_id, -quantity, field='current_stock')

        # Create Waste Record
        waste_record = WasteRecordRepository.create_waste_record(
            inventory_id=inventory_id,
            quantity=quantity,
            reason=reason,
            user_id=user_id,
            remarks=remarks,
            image=image
        )

        # Create Transaction
        transaction_record = StockTransactionRepository.create_transaction(
            inventory_id=inventory_id,
            transaction_type=StockTransaction.TransactionType.WASTE,
            quantity=quantity,
            user_id=user_id,
            source_id=inventory.branch_id,
            remarks=remarks
        )

        # Deduct from FIFO batches
        remaining_qty = quantity
        batches = InventoryBatchRepository.get_active_batches_fifo(inventory_id)
        for batch in batches:
            if remaining_qty <= Decimal('0.00'):
                break
            deduct_qty = min(batch.quantity, remaining_qty)
            InventoryBatchRepository.update_batch_quantity(batch.id, -deduct_qty)
            remaining_qty -= deduct_qty

        # Emit Signals
        stock_updated.send(sender=InventoryService, inventory=inventory, transaction=transaction_record, quantity_change=-quantity)
        waste_recorded.send(sender=InventoryService, waste_record=waste_record)
        
        if inventory.current_stock <= inventory.reorder_level:
            low_stock.send(sender=InventoryService, inventory=inventory)
            
        return waste_record

    @staticmethod
    @transaction.atomic
    def reserve_stock(inventory_id: str, quantity: Decimal) -> None:
        inventory = InventoryRepository.get_by_id(inventory_id)
        validate_stock_availability(inventory, quantity)
        InventoryRepository.update_stock_atomic(inventory_id, quantity, field='reserved_stock')
        InventoryRepository.update_stock_atomic(inventory_id, -quantity, field='current_stock')

    @staticmethod
    @transaction.atomic
    def release_stock(inventory_id: str, quantity: Decimal) -> None:
        InventoryRepository.update_stock_atomic(inventory_id, -quantity, field='reserved_stock')
        InventoryRepository.update_stock_atomic(inventory_id, quantity, field='current_stock')
