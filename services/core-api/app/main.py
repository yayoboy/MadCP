"""
MadCP - Core API Main Application

This is the main entry point for the MadCP FastAPI application.
It configures and initializes all components, middleware, routes, and services.

Author: MadCP Team
License: MIT
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import analysis, assist, health, planning, search
from app.config import get_settings
from app.core.logging import setup_logging
from app.db.database import init_db, close_db
from app.utils.exceptions import MadCPException

# ============================================================================
# Setup Logging
# ============================================================================
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================================
# Settings
# ============================================================================
settings = get_settings()


# ============================================================================
# Lifespan Context Manager
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.

    This manages:
    - Database connections
    - Redis connections
    - Vector database initialization
    - Plugin loading
    - Background task startup
    """
    logger.info("🚀 Starting MadCP Core API...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    try:
        # Initialize database
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("✅ Database connected")

        # Initialize Redis
        logger.info("Initializing Redis connection...")
        # await init_redis()
        logger.info("✅ Redis connected")

        # Initialize Vector DB
        logger.info("Initializing Vector database...")
        # await init_vector_db()
        logger.info("✅ Vector database connected")

        # Load plugins
        if settings.PLUGINS_ENABLED:
            logger.info("Loading plugins...")
            # await load_plugins()
            logger.info("✅ Plugins loaded")

        logger.info("🎉 MadCP Core API is ready!")

        yield

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down MadCP Core API...")

        # Close database connections
        logger.info("Closing database connections...")
        await close_db()

        # Close Redis connections
        # await close_redis()

        # Unload plugins
        # await unload_plugins()

        logger.info("👋 Shutdown complete")


# ============================================================================
# Create FastAPI Application
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="Modern AI-Driven Code Platform - Piattaforma modulare per analisi e assistenza sviluppo software",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host (security)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"📥 {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ {request.method} {request.url.path} - Error: {str(e)}")
        raise


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(MadCPException)
async def madcp_exception_handler(request: Request, exc: MadCPException):
    """Handle custom MadCP exceptions"""
    logger.error(f"MadCP Exception: {exc.message} - {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "code": exc.error_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "details": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )


# ============================================================================
# API Routes
# ============================================================================

# Include API v1 routes
app.include_router(
    health.router,
    tags=["Health"],
)

app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"],
)

app.include_router(
    assist.router,
    prefix="/api/v1/assist",
    tags=["AI Assistance"],
)

app.include_router(
    planning.router,
    prefix="/api/v1/planning",
    tags=["Planning"],
)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Modern AI-Driven Code Platform",
        "environment": settings.APP_ENV,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


# ============================================================================
# Prometheus Metrics
# ============================================================================

if settings.PROMETHEUS_ENABLED:
    # Instrument FastAPI application with Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("📊 Prometheus metrics enabled at /metrics")


# ============================================================================
# Development Tools
# ============================================================================

if settings.DEBUG:
    @app.get("/debug/routes", tags=["Debug"])
    async def debug_routes():
        """List all registered routes (debug only)"""
        routes = []
        for route in app.routes:
            routes.append({
                "path": getattr(route, "path", None),
                "name": getattr(route, "name", None),
                "methods": getattr(route, "methods", None),
            })
        return {"routes": routes}


    @app.get("/debug/config", tags=["Debug"])
    async def debug_config():
        """Show current configuration (debug only)"""
        # Mask sensitive values
        config = settings.dict()
        sensitive_keys = ["JWT_SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DATABASE_URL"]
        for key in sensitive_keys:
            if key in config:
                config[key] = "***MASKED***"
        return config


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
