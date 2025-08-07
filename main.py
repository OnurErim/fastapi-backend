import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from database import Base, engine
from exceptions import register_exception_handlers
from auth import router as auth_router, create_admin_if_not_exists
from users import router as users_router
from announcement_router import router as announcements_router
from sector_router import router as sectors_router

load_dotenv()
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"
PORT = int(os.getenv("PORT", 8000))
MAX_BODY_SIZE_MB = int(os.getenv("MAX_BODY_SIZE_MB", 1))

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

class SuspiciousURLBlockerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        url_path = request.url.path
        url_str = str(request.url)

        if url_path.startswith(("/docs", "/redoc", "/openapi.json", "/favicon.ico")):
            return await call_next(request)

        if any(char in url_str for char in ["?", "&", "<", ">", "script"]):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Geçersiz veya güvenli olmayan bağlantı."}
            )

        return await call_next(request)

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        max_body_size = MAX_BODY_SIZE_MB * 1024 * 1024
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_body_size:
            return JSONResponse(
                status_code=200,
                content={"success": False, "error": "İstek boyutu çok büyük."}
            )
        return await call_next(request)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔄 Uygulama başlatılıyor…")
    if DEBUG:
        Base.metadata.create_all(bind=engine)
        create_admin_if_not_exists()
    yield
    logger.info("🛑 Uygulama kapatılıyor…")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Announcement API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.state.limiter = limiter

app.add_middleware(SuspiciousURLBlockerMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://frontend.domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router,      prefix="/auth")
app.include_router(users_router,     prefix="/users")
app.include_router(announcements_router)
app.include_router(sectors_router,   prefix="/sectors")

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "version": app.version,
        "env": ENV,
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    filtered_routes = [
        r for r in app.routes
        if isinstance(r, APIRoute)
        and r.tags
        and "Health" not in r.tags
    ]

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=filtered_routes,
    )

    schema["info"]["x-logo"] = {
        "url": "https://i.imgur.com/qgKrkU7.png"
    }

    schema["x-tagGroups"] = [
        {"name": "Kimlik İşlemleri", "tags": ["Auth"]},
        {"name": "Kullanıcı İşlemleri", "tags": ["Users"]},
        {"name": "Duyurular", "tags": [
            "Public Announcements",
            "Admin Announcements",
            "User Announcements",
            "Saved Announcements"
        ]},
        {"name": "Sektörler", "tags": ["Sectors"]}
    ]

    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        log_level="debug",
    )