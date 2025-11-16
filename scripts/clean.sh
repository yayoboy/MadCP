#!/bin/bash
# ============================================================================
# MadCP - Clean Script
# ============================================================================
#
# This script cleans up MadCP development environment
#
# Usage:
#   ./scripts/clean.sh [option]
#
# Options:
#   all    - Remove everything (containers, volumes, images, data)
#   soft   - Remove only containers and temporary files
#   data   - Remove only data directories
#
# ============================================================================

set -e

CLEAN_TYPE=${1:-soft}

echo "🧹 Cleaning MadCP environment..."

case "$CLEAN_TYPE" in
    all)
        echo "⚠️  This will remove EVERYTHING (containers, volumes, images, data)"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Stopping and removing all containers..."
            docker-compose down -v

            echo "Removing Docker images..."
            docker images | grep madcp | awk '{print $3}' | xargs -r docker rmi -f

            echo "Removing data directories..."
            rm -rf data/ logs/

            echo "✅ Complete cleanup done!"
        else
            echo "❌ Cleanup cancelled"
        fi
        ;;

    soft)
        echo "Stopping containers..."
        docker-compose down

        echo "Removing Python cache files..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        find . -type f -name "*.pyo" -delete 2>/dev/null || true

        echo "Removing logs..."
        rm -rf logs/*.log 2>/dev/null || true

        echo "✅ Soft cleanup done!"
        ;;

    data)
        echo "⚠️  This will remove all data directories"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing data directories..."
            rm -rf data/
            echo "✅ Data cleanup done!"
        else
            echo "❌ Cleanup cancelled"
        fi
        ;;

    *)
        echo "Unknown option: $CLEAN_TYPE"
        echo "Use: all, soft, or data"
        exit 1
        ;;
esac
