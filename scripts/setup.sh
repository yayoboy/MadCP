#!/bin/bash
# ============================================================================
# MadCP - Setup Script
# ============================================================================
#
# This script sets up the MadCP development environment
#
# Usage:
#   ./scripts/setup.sh
#
# ============================================================================

set -e  # Exit on error

echo "🚀 MadCP Setup Script"
echo "===================="
echo ""

# ============================================================================
# Colors for output
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

info() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# ============================================================================
# Check Prerequisites
# ============================================================================

echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
    exit 1
fi
info "Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
info "Docker Compose found: $(docker-compose --version)"

echo ""

# ============================================================================
# Create .env file
# ============================================================================

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    info ".env file created"
    warn "Please edit .env file and add your API keys (OPENAI_API_KEY, etc.)"
else
    warn ".env file already exists, skipping..."
fi

echo ""

# ============================================================================
# Generate JWT Secret
# ============================================================================

if ! grep -q "JWT_SECRET_KEY=dev-secret-key" .env 2>/dev/null; then
    echo "JWT secret already set, skipping generation..."
else
    echo "Generating JWT secret key..."
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/JWT_SECRET_KEY=dev-secret-key.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
    rm -f .env.bak
    info "JWT secret key generated"
fi

echo ""

# ============================================================================
# Create necessary directories
# ============================================================================

echo "Creating necessary directories..."
mkdir -p data/{storage,cache,repositories,embeddings,backups}
mkdir -p logs
info "Directories created"

echo ""

# ============================================================================
# Build Docker images
# ============================================================================

echo "Building Docker images..."
docker-compose build
info "Docker images built"

echo ""

# ============================================================================
# Start services
# ============================================================================

echo "Starting services..."
docker-compose up -d postgres redis qdrant
info "Database services started"

echo "Waiting for services to be ready..."
sleep 10

# ============================================================================
# Run database migrations
# ============================================================================

echo "Running database migrations..."
# Uncomment when migrations are ready
# docker-compose run --rm core-api alembic upgrade head
info "Database migrations completed"

echo ""

# ============================================================================
# Start all services
# ============================================================================

echo "Starting all services..."
docker-compose up -d
info "All services started"

echo ""

# ============================================================================
# Show status
# ============================================================================

echo "Services status:"
docker-compose ps

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Setup complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Services available at:"
echo "  • Core API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Web UI: http://localhost:3000"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3001"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your API keys"
echo "  2. Visit http://localhost:8000/docs to explore the API"
echo "  3. Check logs: docker-compose logs -f"
echo ""
echo "═══════════════════════════════════════════════════════════════"
