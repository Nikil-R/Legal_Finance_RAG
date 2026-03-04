"""
Middleware for error handling, logging, and CORS.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import time
import traceback
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all incoming requests and their processing time.
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(start_time * 1000)}"
        
        # Log incoming request
        logger.info(
            "Request started | ID: %s | Method: %s | Path: %s",
            request_id, request.method, request.url.path
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (time.time() - start_time) * 1000
            
            # Log completed request
            logger.info(
                "Request completed | ID: %s | Status: %d | Time: %.2fms",
                request_id, response.status_code, process_time
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(int(process_time))
            
            return response
        
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "Request failed | ID: %s | Error: %s | Time: %.2fms",
                request_id, str(e), process_time
            )
            raise


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.
    """
    logger.error("Unhandled exception: %s\n%s", str(exc), traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "error_type": "internal_error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_type": "http_error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
