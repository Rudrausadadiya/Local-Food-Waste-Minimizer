from django.core.exceptions import ValidationError
from decimal import Decimal

def validate_business_active(business):
    if not getattr(business, 'is_active', True):
        raise ValidationError("Inactive businesses cannot publish listings.")

def validate_inventory_for_listing(product, requested_quantity: int, branch_id: str):
    from apps.inventory.models import Inventory
    
    if getattr(product, 'is_deleted', False) or not getattr(product, 'is_active', True):
        raise ValidationError("Cannot list inactive or deleted products.")

    inventory = Inventory.objects.filter(product_id=product.id, branch_id=branch_id).first()
    if not inventory:
        raise ValidationError("No inventory found for this product.")
        
    available_stock = inventory.current_stock - inventory.reserved_stock
    if requested_quantity > available_stock:
        raise ValidationError(f"Requested quantity ({requested_quantity}) exceeds available unreserved stock ({available_stock}).")

def validate_inventory_batch(batch):
    from django.utils import timezone
    if batch and batch.expiry_date and batch.expiry_date < timezone.now().date():
        raise ValidationError("Expired inventory cannot be listed.")
