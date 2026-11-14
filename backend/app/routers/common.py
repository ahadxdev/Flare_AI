from app.models import ErrorResponse


ERROR_RESPONSES = {
    404: {"model": ErrorResponse, "description": "Requested record was not found."},
    422: {"model": ErrorResponse, "description": "Request validation failed."},
    500: {"model": ErrorResponse, "description": "Unexpected server error."},
}
