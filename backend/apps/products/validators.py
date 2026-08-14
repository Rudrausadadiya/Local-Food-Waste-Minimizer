from django.core.exceptions import ValidationError

# Function: validate_positive_price
def validate_positive_price(value):
    if value < 0:
        raise ValidationError('Price must be positive.')
