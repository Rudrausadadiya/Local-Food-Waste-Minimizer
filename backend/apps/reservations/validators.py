from django.core.exceptions import ValidationError

# Function: validate_product_active
def validate_product_active(product):
    if getattr(product, 'is_deleted', False):
        raise ValidationError(f"Product {product.name} is deleted and cannot be reserved.")
    if not getattr(product, 'is_active', True):
        raise ValidationError(f"Product {product.name} is inactive and cannot be reserved.")

# Function: validate_reservation_modifiable
def validate_reservation_modifiable(reservation):
    if reservation.reservation_status in ['COMPLETED', 'CANCELLED', 'EXPIRED']:
        raise ValidationError(f"Cannot modify a {reservation.reservation_status.lower()} reservation.")
