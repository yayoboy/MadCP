#!/bin/bash
# ============================================================================
# MadCP - Development Script
# ============================================================================
#
# This script starts MadCP in development mode with hot reload
#
# Usage:
#   ./scripts/dev.sh
#
# ============================================================================

set -e

echo "🔧 Starting MadCP in development mode..."

# Start services with dev configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Alternatively, to run in detached mode:
# docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
