from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded

def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        temiz_mesajlar = []
        for err in exc.errors():
            msg = err.get("msg", "")
            
            if "Value error" in msg:
                msg = msg.split(", ", 1)[-1]  
            elif "string does not match regex" in msg.lower():
                msg = "Geçersiz format"
            temiz_mesajlar.append(msg)

        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "message": "Lütfen formu kontrol edin. Bazı alanlarda eksik veya hatalı bilgi var.",
                "details": temiz_mesajlar
            }
        )

    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "message": "Çok fazla istek gönderildi. Lütfen biraz bekleyin."
            }
        )

    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Beklenmeyen bir hata oluştu.",
                "error": str(exc),
                "path": request.url.path
            }
        )