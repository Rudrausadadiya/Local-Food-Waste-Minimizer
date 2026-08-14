import logging
from rest_framework.views import exception_handler
from common.responses import error_response

logger = logging.getLogger('django')

# Function: custom_exception_handler
def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework that standardizes 
    all errors into a common format.
    """
    from django.core.exceptions import ValidationError as DjangoValidationError
    from rest_framework.exceptions import ValidationError as DRFValidationError

    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            exc = DRFValidationError(exc.message_dict)
        elif hasattr(exc, 'messages'):
            exc = DRFValidationError(exc.messages)
        else:
            exc = DRFValidationError(str(exc))

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # It's a standard DRF exception
        error_code = getattr(exc, 'default_code', 'error')
        status_code = response.status_code
        
        # Flatten validation errors
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = response.data['detail']
            else:
                first_field = next(iter(response.data))
                val = response.data[first_field]
                first_msg = val[0] if isinstance(val, list) and val else str(val)
                message = f"{first_field}: {first_msg}"
            details = response.data
        elif isinstance(response.data, list):
            message = response.data[0] if response.data else "Error"
            details = response.data
        else:
            message = str(response.data)
            details = None

        return error_response(
            message=str(message),
            errors=details,
            status_code=status_code,
            code=error_code
        )
    
    # Non-DRF exception (Internal Server Error)
    logger.exception(f"Unhandled exception: {exc}")
    
    return error_response(
        message="An unexpected error occurred.",
        errors=str(exc) if context.get('request').META.get('SERVER_NAME') in ['localhost', '127.0.0.1'] else None, # Only expose details in dev
        status_code=500,
        code='internal_server_error'
    )
