"""
app/main.py — FastAPI application factory.
Run with: uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.logger import setup_logging, get_logger
from app.db.session import engine
from app.models.base import Base
from app.db.seed import seed_database
from app.api.routes import plans, changes, rag, reports, scrape, isps
from app.api.middleware.request_logger import request_logger_middleware

settings = get_settings()
logger   = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging()
    logger.info("cip_starting", env=settings.app_env, port=settings.app_port)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    
    from app.db.session import get_sync_db
    session = next(get_sync_db())
    seed_database(session)
    session.close()
    logger.info("cip_ready")

    yield

    logger.info("cip_shutting_down")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="WorldLink CIP — Competitive Intelligence Platform",
        description=(
            "Internal API for tracking competitor ISPs "
            "(Vianet, Subisu, DishHome, CG Net) and generating intelligence."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

   
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

   
    app.add_middleware(BaseHTTPMiddleware, dispatch=request_logger_middleware)

    # Health check
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "env": settings.app_env}

    # Routers
    app.include_router(plans.router)
    app.include_router(changes.router)
    app.include_router(rag.router)
    app.include_router(reports.router)
    app.include_router(scrape.router)
    app.include_router(isps.router)

    return app


app = create_app()
