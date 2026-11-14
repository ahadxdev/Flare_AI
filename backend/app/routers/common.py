from app.models import ErrorResponse


ERROR_RESPONSES = {
    404: {"model": ErrorResponse, "description": "Requested record was not found."},
    422: {"model": ErrorResponse, "description": "Request validation or evidence error."},
    500: {"model": ErrorResponse, "description": "Unexpected server error."},
}
