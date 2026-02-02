from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize the error response
        data = response.data
        formatted_errors = []

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for v in value:
                        formatted_errors.append({
                            'code': 'validation_error',
                            'detail': str(v),
                            'attr': key
                        })
                else:
                     formatted_errors.append({
                        'code': 'error',
                        'detail': str(value),
                        'attr': key
                    })
        elif isinstance(data, list):
            for value in data:
                formatted_errors.append({
                    'code': 'error',
                    'detail': str(value),
                    'attr': None
                })

        response.data = {
            'type': 'client_error' if response.status_code < 500 else 'server_error',
            'errors': formatted_errors
        }

    return response
