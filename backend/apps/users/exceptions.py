from rest_framework.exceptions import APIException
from rest_framework import status

# Class: UserException
class UserException(APIException):
    """Base exception for user related errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'user_error'

# Class: UserNotFound
class UserNotFound(UserException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'User not found.'
    default_code = 'user_not_found'

# Class: UserAlreadyExists
class UserAlreadyExists(UserException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A user with this email already exists.'
    default_code = 'user_already_exists'

# Class: InvalidCredentials
class InvalidCredentials(UserException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid email or password.'
    default_code = 'invalid_credentials'

# Class: EmailNotVerified
class EmailNotVerified(UserException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Please verify your email address.'
    default_code = 'email_not_verified'

# Class: AccountInactive
class AccountInactive(UserException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'This account has been deactivated.'
    default_code = 'account_inactive'
