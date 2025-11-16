# ============================================================================
# MadCP - Core API Dockerfile
# ============================================================================
#
# Multi-stage build for optimized production images
#
# Stages:
#   - base: Common base with Python and system dependencies
#   - development: Development environment with dev tools
#   - production: Optimized production image
#
# ============================================================================

# ============================================================================
# Base Stage - Common Dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    # Git (for repository cloning)
    git \
    # curl for health checks
    curl \
    # PostgreSQL client
    libpq-dev \
    # Tree-sitter build dependencies
    cmake \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN groupadd -r madcp && useradd -r -g madcp madcp
RUN mkdir -p /app && chown -R madcp:madcp /app

WORKDIR /app

# ============================================================================
# Development Stage
# ============================================================================
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (will be overridden by volume mount in dev)
COPY . .

# Change ownership
RUN chown -R madcp:madcp /app

# Switch to app user
USER madcp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Builder Stage - Build Dependencies
# ============================================================================
FROM base as builder

# Copy requirements
COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Production Stage
# ============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r madcp && useradd -r -g madcp madcp

# Create app directory
RUN mkdir -p /app && chown -R madcp:madcp /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=madcp:madcp . .

# Switch to app user
USER madcp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ============================================================================
# Metadata
# ============================================================================
LABEL maintainer="MadCP Team" \
      version="1.0.0" \
      description="MadCP Core API Service"
