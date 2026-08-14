from django.core.exceptions import ValidationError

# Function: validate_date_range
def validate_date_range(start_date, end_date):
    if start_date and end_date:
        if start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")
        
        # Limit max query window to 2 years to prevent DB strain
        if (end_date - start_date).days > 730:
            raise ValidationError("Date range cannot exceed 2 years.")
