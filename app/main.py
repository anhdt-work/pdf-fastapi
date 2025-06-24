from fastapi import FastAPI
import uvicorn
import logging
from app.routers import pdf_router, gcs_router
from app.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    # Include routers
    app.include_router(
        pdf_router.router,
        prefix=settings.API_PREFIX,
        tags=["PDF"]
    )
    
    app.include_router(
        gcs_router.router,
        prefix=settings.API_PREFIX,
        tags=["Google Cloud Storage"]
    )
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 