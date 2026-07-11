from django.core.exceptions import ValidationError
from .models import OrderStatus

def validate_order_modifiable(order):
    if order.order_status == OrderStatus.COMPLETED:
        raise ValidationError("Cannot modify completed orders.")
    if order.order_status == OrderStatus.CANCELLED:
        raise ValidationError("Cannot modify cancelled orders.")
