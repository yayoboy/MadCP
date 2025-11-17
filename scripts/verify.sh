#!/bin/bash
# ============================================================================
# MadCP - Verification Script
# ============================================================================
#
# Verifica che tutti i servizi MadCP siano operativi
#
# Usage:
#   ./scripts/verify.sh
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
MAX_WAIT=120  # Maximum wait time in seconds
WAIT_INTERVAL=5

# ============================================================================
# Functions
# ============================================================================

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 non trovato. Installalo prima di continuare."
        exit 1
    fi
}

wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=$((MAX_WAIT / WAIT_INTERVAL))
    local attempt=1

    info "Attendo che $service_name sia pronto..."

    while [ $attempt -le $max_attempts ]; do
        if eval $check_command &> /dev/null; then
            success "$service_name è pronto!"
            return 0
        fi

        echo -n "."
        sleep $WAIT_INTERVAL
        attempt=$((attempt + 1))
    done

    error "$service_name non risponde dopo ${MAX_WAIT}s"
    return 1
}

# ============================================================================
# Main
# ============================================================================

echo "═══════════════════════════════════════════════════════════════"
echo "  MadCP - Verifica Sistema"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check required commands
info "Controllo comandi richiesti..."
check_command docker
check_command curl
success "Comandi richiesti presenti"
echo ""

# Check Docker is running
info "Verifico che Docker sia in esecuzione..."
if ! docker info &> /dev/null; then
    error "Docker non è in esecuzione"
    exit 1
fi
success "Docker è in esecuzione"
echo ""

# Check if containers are running
info "Verifico container MadCP..."

declare -A containers=(
    ["madcp-postgres"]="Database PostgreSQL"
    ["madcp-redis"]="Redis Cache"
    ["madcp-qdrant"]="Qdrant Vector DB"
    ["madcp-core-api"]="Core API"
)

all_running=true
for container in "${!containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        success "${containers[$container]} ($container) è in esecuzione"
    else
        warning "${containers[$container]} ($container) NON è in esecuzione"
        all_running=false
    fi
done
echo ""

if [ "$all_running" = false ]; then
    error "Alcuni container non sono in esecuzione"
    info "Avviali con: docker-compose up -d"
    exit 1
fi

# Check health status
info "Verifico health status dei container..."

for container in "${!containers[@]}"; do
    health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no-health-check")

    if [ "$health" = "healthy" ]; then
        success "${containers[$container]}: healthy"
    elif [ "$health" = "starting" ]; then
        warning "${containers[$container]}: starting (attendi...)"
    elif [ "$health" = "no-health-check" ]; then
        info "${containers[$container]}: nessun health check configurato"
    else
        error "${containers[$container]}: $health"
    fi
done
echo ""

# Wait for services to be ready
info "Attendo che tutti i servizi siano pronti..."
echo ""

# Wait for PostgreSQL
wait_for_service "PostgreSQL" "docker exec madcp-postgres pg_isready -U madcp -q"

# Wait for Redis
wait_for_service "Redis" "docker exec madcp-redis redis-cli ping | grep -q PONG"

# Wait for Qdrant
wait_for_service "Qdrant" "curl -sf ${API_URL/8000/6333}/"

# Wait for Core API
wait_for_service "Core API" "curl -sf $API_URL/health"

echo ""

# Test API endpoints
info "Testo API endpoints..."
echo ""

# Health endpoint
if response=$(curl -sf "$API_URL/health"); then
    success "Health endpoint: OK"
    echo "   Response: $response" | head -c 100
    echo "..."
else
    error "Health endpoint: FAILED"
fi

# Detailed health endpoint
if response=$(curl -sf "$API_URL/health/detailed"); then
    success "Detailed health endpoint: OK"
else
    warning "Detailed health endpoint: FAILED (potrebbe essere normale se i servizi stanno ancora inizializzando)"
fi

# API documentation
if curl -sf "$API_URL/docs" > /dev/null; then
    success "API documentation: OK"
else
    warning "API documentation: Non accessibile"
fi

# Root endpoint
if curl -sf "$API_URL/" > /dev/null; then
    success "Root endpoint: OK"
else
    warning "Root endpoint: Non accessibile"
fi

echo ""

# Check logs for errors
info "Verifico gli ultimi log per errori..."
echo ""

for container in madcp-core-api madcp-postgres madcp-redis madcp-qdrant; do
    if docker logs --tail=50 $container 2>&1 | grep -qi "error\|exception\|fatal"; then
        warning "$container ha degli errori nei log recenti"
        echo "   Ultimi errori:"
        docker logs --tail=10 $container 2>&1 | grep -i "error\|exception\|fatal" | head -3
    else
        success "$container: nessun errore nei log recenti"
    fi
done

echo ""

# Network connectivity test
info "Testo connettività tra container..."

# Test Core API -> PostgreSQL
if docker exec madcp-core-api sh -c "curl -sf http://postgres:5432 > /dev/null 2>&1 || nc -zv postgres 5432 > /dev/null 2>&1"; then
    success "Core API -> PostgreSQL: OK"
else
    warning "Core API -> PostgreSQL: Connessione fallita"
fi

# Test Core API -> Redis
if docker exec madcp-core-api sh -c "curl -sf http://redis:6379 > /dev/null 2>&1 || nc -zv redis 6379 > /dev/null 2>&1"; then
    success "Core API -> Redis: OK"
else
    warning "Core API -> Redis: Connessione fallita"
fi

# Test Core API -> Qdrant
if docker exec madcp-core-api curl -sf http://qdrant:6333/ > /dev/null 2>&1; then
    success "Core API -> Qdrant: OK"
else
    warning "Core API -> Qdrant: Connessione fallita"
fi

echo ""

# Volume check
info "Verifico volumi Docker..."
echo ""

volumes=$(docker volume ls --format '{{.Name}}' | grep madcp || docker volume ls --format '{{.Name}}' | grep -E 'postgres_data|redis_data|qdrant_data')

if [ -n "$volumes" ]; then
    success "Volumi trovati:"
    echo "$volumes" | while read volume; do
        size=$(docker volume inspect $volume --format '{{.Mountpoint}}' | xargs du -sh 2>/dev/null | cut -f1 || echo "N/A")
        echo "   - $volume: $size"
    done
else
    warning "Nessun volume MadCP trovato"
fi

echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo "  Riepilogo"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Final check
all_healthy=true

for container in "${!containers[@]}"; do
    health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "running")
    if [ "$health" != "healthy" ] && [ "$health" != "running" ]; then
        all_healthy=false
        break
    fi
done

if [ "$all_healthy" = true ]; then
    success "Tutti i servizi sono operativi!"
    echo ""
    info "Puoi accedere a:"
    echo "   • API: $API_URL"
    echo "   • Documentazione: $API_URL/docs"
    echo "   • Health check: $API_URL/health"
    echo ""
    info "Comandi utili:"
    echo "   • docker-compose ps        # Stato servizi"
    echo "   • docker-compose logs -f   # Segui i log"
    echo "   • docker-compose down      # Ferma tutto"
    echo ""
    exit 0
else
    error "Alcuni servizi hanno problemi"
    echo ""
    info "Suggerimenti:"
    echo "   1. Controlla i log: docker-compose logs -f"
    echo "   2. Verifica variabili .env"
    echo "   3. Riavvia i servizi: docker-compose restart"
    echo ""
    exit 1
fi
