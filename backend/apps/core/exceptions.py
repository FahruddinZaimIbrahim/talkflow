from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
            }
        }
        
        if hasattr(response, 'data') and isinstance(response.data, dict):
            custom_response['error']['details'] = response.data
        
        response.data = custom_response
        
        # Log error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={'context': context}
        )
    
    return response


class LLMServiceException(Exception):
    """Custom exception for LLM service errors"""
    pass


class ConversationNotFoundException(Exception):
    """Raised when conversation is not found"""
    pass