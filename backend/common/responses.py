from rest_framework.response import Response
from rest_framework import status

# Function: success_response
def success_response(data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
    """
    Standardize success responses across the application.
    """
    response_data = {
        "success": True,
        "message": message,
        "data": data,
    }
    
    if meta:
        response_data["meta"] = meta
        
    return Response(response_data, status=status_code)

# Function: error_response
def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, code="error"):
    """
    Standardize error responses across the application.
    """
    response_data = {
        "success": False,
        "message": message,
        "code": code,
        "errors": errors,
    }
    return Response(response_data, status=status_code)
