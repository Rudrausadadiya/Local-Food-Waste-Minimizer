from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import InventoryBatch

def validate_transfer_businesses(inventory_from, inventory_to):
    """Ensure stock transfers occur within the same business."""
    if inventory_from.business_id != inventory_to.business_id:
        raise ValidationError(_("Cannot transfer inventory between different businesses."))

def validate_stock_availability(inventory, quantity_required):
    """Ensure sufficient available stock."""
    if inventory.available_stock < quantity_required:
        raise ValidationError(
            _("Insufficient available stock. Have %(available)s, need %(required)s."),
            params={'available': inventory.available_stock, 'required': quantity_required}
        )

def validate_reserve_stock(inventory, reserve_quantity):
    """Ensure cannot reserve more stock than available."""
    if inventory.available_stock < reserve_quantity:
        raise ValidationError(
            _("Cannot reserve more stock than available. Available: %(available)s"),
            params={'available': inventory.available_stock}
        )

def validate_unique_batch(inventory_id, batch_number):
    """Ensure batch numbers are unique for a specific inventory (product/branch)."""
    if InventoryBatch.objects.filter(inventory_id=inventory_id, batch_number=batch_number).exists():
        raise ValidationError(_("Batch number %(batch)s already exists for this inventory."), params={'batch': batch_number})
