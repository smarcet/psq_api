from rest_framework import views
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = views.exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        response.status_code = 412
    return response
