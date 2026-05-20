"""Request timing middleware."""
import time
from fastapi import Request
from app.logger import get_logger

logger = get_logger(__name__)

async def request_logger_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info("http_request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=duration)
    return response
