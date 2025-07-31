import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def debug_request_middleware(request: Request, call_next):
    """
    Debug middleware for logging HTTP requests and responses.

    This middleware logs:
    - Incoming request method and URL path
    - Response status code
    - Any errors that occur during request processing

    Args:
        request: FastAPI Request object
        call_next: Next middleware/handler in the chain

    Returns:
        Response from the next handler
    """
    logger.debug(f"Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise
