from django.core.exceptions import ValidationError

# Function: validate_ngo_verified
def validate_ngo_verified(ngo):
    from .models import NGOVerificationStatus
    if ngo.verification_status != NGOVerificationStatus.VERIFIED:
        raise ValidationError("Only verified NGOs can request donations.")

# Function: validate_inventory_for_donation
def validate_inventory_for_donation(product, branch_id: str, requested_quantity: int):
    from apps.inventory.models import Inventory
    
    if getattr(product, 'is_deleted', False) or not getattr(product, 'is_active', True):
        raise ValidationError("Cannot donate inactive or deleted products.")

    inventory = Inventory.objects.filter(product_id=product.id, branch_id=branch_id).first()
    if not inventory:
        raise ValidationError("No inventory found for this product.")
        
    available_stock = inventory.current_stock - inventory.reserved_stock
    if requested_quantity > available_stock:
        raise ValidationError(f"Quantity ({requested_quantity}) exceeds available unreserved stock ({available_stock}). Reserved inventory cannot be donated.")

# Function: validate_donation_immutable
def validate_donation_immutable(listing):
    from .models import DonationStatus
    if listing.donation_status == DonationStatus.COMPLETED:
        raise ValidationError("Completed donations are immutable.")

# Function: validate_inventory_batch_for_donation
def validate_inventory_batch_for_donation(batch):
    from django.utils import timezone
    if batch and batch.expiry_date and batch.expiry_date < timezone.now().date():
        raise ValidationError("Expired inventory cannot be donated.")
