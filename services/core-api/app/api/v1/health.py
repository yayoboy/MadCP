"""
MadCP - Health Check Endpoints

Provides health check and status endpoints for monitoring and
diagnostics.

Author: MadCP Team
License: MIT
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# ============================================================================
# Response Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status (healthy, unhealthy, degraded)")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")


class DetailedHealthResponse(BaseModel):
    """Detailed health check with service dependencies"""
    status: str = Field(..., description="Overall status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Current timestamp")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Status of dependent services")


class StatusResponse(BaseModel):
    """API status response"""
    name: str
    version: str
    environment: str
    uptime: float
    features: Dict[str, bool]


# ============================================================================
# Health Check Endpoints
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Simple health check endpoint for load balancers and monitoring",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        HealthResponse: Service health status

    This is a lightweight endpoint that returns immediately without
    checking dependencies. Use /health/detailed for comprehensive checks.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Comprehensive health check including all dependent services",
    tags=["Health"],
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check with dependency status.

    Checks the status of:
    - Database connection
    - Redis connection
    - Vector database connection
    - Plugin system

    Returns:
        DetailedHealthResponse: Comprehensive health status

    Status meanings:
    - healthy: All services operational
    - degraded: Some non-critical services unavailable
    - unhealthy: Critical services unavailable
    """
    services_status = {}
    overall_status = "healthy"

    # Check Database
    try:
        # TODO: Implement actual database health check
        # from app.db.database import check_database_health
        # db_healthy = await check_database_health()
        db_healthy = True

        services_status["database"] = {
            "status": "connected" if db_healthy else "disconnected",
            "checked_at": datetime.utcnow().isoformat(),
        }

        if not db_healthy:
            overall_status = "unhealthy"

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        services_status["database"] = {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }
        overall_status = "unhealthy"

    # Check Redis
    try:
        # TODO: Implement actual Redis health check
        # from app.db.redis import check_redis_health
        # redis_healthy = await check_redis_health()
        redis_healthy = True

        services_status["redis"] = {
            "status": "connected" if redis_healthy else "disconnected",
            "checked_at": datetime.utcnow().isoformat(),
        }

        if not redis_healthy and overall_status == "healthy":
            overall_status = "degraded"

    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        services_status["redis"] = {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }
        if overall_status == "healthy":
            overall_status = "degraded"

    # Check Vector Database
    try:
        # TODO: Implement actual vector DB health check
        # from app.db.vector_db import check_vector_db_health
        # vector_db_healthy = await check_vector_db_health()
        vector_db_healthy = True

        services_status["vector_db"] = {
            "status": "connected" if vector_db_healthy else "disconnected",
            "checked_at": datetime.utcnow().isoformat(),
        }

        if not vector_db_healthy and overall_status == "healthy":
            overall_status = "degraded"

    except Exception as e:
        logger.error(f"Vector DB health check failed: {str(e)}")
        services_status["vector_db"] = {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }
        if overall_status == "healthy":
            overall_status = "degraded"

    # Check Plugin System
    if settings.PLUGINS_ENABLED:
        try:
            # TODO: Implement plugin system health check
            plugins_healthy = True

            services_status["plugins"] = {
                "status": "active" if plugins_healthy else "inactive",
                "checked_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Plugin health check failed: {str(e)}")
            services_status["plugins"] = {
                "status": "error",
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat(),
            }

    return DetailedHealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services=services_status,
    )


@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="API status",
    description="Get API status and enabled features",
    tags=["Health"],
)
async def get_status() -> StatusResponse:
    """
    Get API status and configuration.

    Returns:
        StatusResponse: API status and features

    This endpoint provides:
    - API version
    - Environment
    - Uptime
    - Enabled features
    """
    import time
    import psutil

    # Calculate uptime (approximate - from process start)
    process = psutil.Process()
    uptime = time.time() - process.create_time()

    return StatusResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        uptime=uptime,
        features={
            "semantic_search": settings.FEATURE_SEMANTIC_SEARCH,
            "code_analysis": settings.FEATURE_CODE_ANALYSIS,
            "ai_assistance": settings.FEATURE_AI_ASSISTANCE,
            "planning": settings.FEATURE_PLANNING,
            "plugins": settings.PLUGINS_ENABLED,
        },
    )


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint",
    tags=["Health"],
)
async def readiness_probe():
    """
    Readiness probe for Kubernetes.

    Returns 200 if the service is ready to accept traffic,
    503 otherwise.

    This checks if critical dependencies are available.
    """
    # Check critical dependencies
    try:
        # TODO: Add actual dependency checks
        # - Database connection
        # - Redis connection
        # - Configuration loaded
        is_ready = True

        if is_ready:
            return {"status": "ready"}
        else:
            return {"status": "not ready"}, status.HTTP_503_SERVICE_UNAVAILABLE

    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return {"status": "error", "message": str(e)}, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint",
    tags=["Health"],
)
async def liveness_probe():
    """
    Liveness probe for Kubernetes.

    Returns 200 if the service is alive, indicating the container
    should not be restarted.

    This is a simple check that the application is running.
    """
    return {"status": "alive"}


# ============================================================================
# Export
# ============================================================================

__all__ = ["router"]
