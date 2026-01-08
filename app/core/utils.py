import uuid
from django.http import JsonResponse

def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())

def create_response(data=None, message="", status=200, success=True):
    """
    Helper to create a standardized JSON response.
    """
    response_data = {
        "success": success,
        "message": message,
        "data": data,
    }
    return JsonResponse(response_data, status=status)
