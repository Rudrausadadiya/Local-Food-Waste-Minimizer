import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
import pytz

def validate_gst(value: str) -> None:
    if value and not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', value):
        raise ValidationError("Invalid GST number format.")

def validate_phone(value: str) -> None:
    if value and not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

def validate_currency(value: str) -> None:
    # Basic check, can be expanded to a real ISO currency list
    if value and len(value) != 3:
        raise ValidationError("Currency must be a 3-letter ISO code.")

def validate_timezone(value: str) -> None:
    if value and value not in pytz.all_timezones:
        raise ValidationError("Invalid timezone string.")

def validate_business_email(value: str) -> None:
    validator = EmailValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError("Invalid email format.")

def validate_business_website(value: str) -> None:
    if value:
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise ValidationError("Invalid website URL.")
