import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from common.responses import error_response

logger = logging.getLogger('django')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework that standardizes 
    all errors into a common format.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # It's a standard DRF exception
        error_code = getattr(exc, 'default_code', 'error')
        status_code = response.status_code
        
        # Flatten validation errors
        if isinstance(response.data, dict):
            # Extract standard DRF detail or use the full dictionary for validation errors
            if 'detail' in response.data:
                message = response.data['detail']
            else:
                message = "Validation Error"
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
