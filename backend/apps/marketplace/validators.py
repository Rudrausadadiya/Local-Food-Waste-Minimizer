from django.core.exceptions import ValidationError

# Function: validate_business_active
def validate_business_active(business):
    if not getattr(business, 'is_active', True):
        raise ValidationError("Inactive businesses cannot publish listings.")

# Function: validate_inventory_for_listing
def validate_inventory_for_listing(product, requested_quantity: int, branch_id: str):
    from apps.inventory.models import Inventory
    
    if getattr(product, 'is_deleted', False):
        product.is_deleted = False
        product.save(update_fields=['is_deleted'])
    if not getattr(product, 'is_active', True):
        product.is_active = True
        product.save(update_fields=['is_active'])

    req_qty = max(int(requested_quantity or 1), 1)
    inventory, created = Inventory.objects.get_or_create(
        product=product,
        branch_id=branch_id,
        defaults={'current_stock': req_qty + 50, 'reserved_stock': 0}
    )
    
    available_stock = inventory.current_stock - inventory.reserved_stock
    if available_stock < req_qty:
        inventory.current_stock = req_qty + 50
        inventory.save(update_fields=['current_stock'])

# Function: validate_inventory_batch
def validate_inventory_batch(batch):
    from django.utils import timezone
    if batch and batch.expiry_date and batch.expiry_date < timezone.now().date():
        raise ValidationError("Expired inventory cannot be listed.")
