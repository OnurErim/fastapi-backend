from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class SuspiciousURLBlockerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        url_path = request.url.path
        url_str = str(request.url)

        
        swagger_paths = ["/docs", "/redoc", "/openapi.json"]
        if any(url_path.startswith(path) for path in swagger_paths):
            return await call_next(request)

        
        if any(char in url_str for char in ["?", "&", "<", ">", "script"]):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Geçersiz veya güvenli olmayan bağlantı."}
            )

        return await call_next(request)