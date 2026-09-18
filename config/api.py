from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _validation_details(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"non_field_errors": exc.messages}
    return {"non_field_errors": [str(exc)]}


def api_exception_handler(exc, context):
    """Translate expected Django model errors into stable API responses."""
    response = exception_handler(exc, context)
    if response is not None:
        return response
    if isinstance(exc, DjangoValidationError):
        return Response(_validation_details(exc), status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, ProtectedError):
        return Response(
            {"detail": "This record is still in use and cannot be deleted. Deactivate it instead."},
            status=status.HTTP_409_CONFLICT,
        )
    return None
