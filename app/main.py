from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", description="Local-first grounded RAG API")
app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": settings.app_name, "version": "0.1.0", "docs": "/docs"}
