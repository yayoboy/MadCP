#!/bin/bash
# ============================================================================
# MadCP - Test Script
# ============================================================================
#
# This script runs all tests for MadCP
#
# Usage:
#   ./scripts/test.sh [options]
#
# Options:
#   unit         - Run only unit tests
#   integration  - Run only integration tests
#   e2e          - Run only end-to-end tests
#   coverage     - Run tests with coverage report
#
# ============================================================================

set -e

TEST_TYPE=${1:-all}

echo "🧪 Running MadCP tests..."

case "$TEST_TYPE" in
    unit)
        echo "Running unit tests..."
        docker-compose run --rm core-api pytest tests/unit -v
        ;;
    integration)
        echo "Running integration tests..."
        docker-compose run --rm core-api pytest tests/integration -v
        ;;
    e2e)
        echo "Running end-to-end tests..."
        docker-compose run --rm core-api pytest tests/e2e -v
        ;;
    coverage)
        echo "Running tests with coverage..."
        docker-compose run --rm core-api pytest --cov=app --cov-report=html --cov-report=term
        echo "Coverage report generated in htmlcov/"
        ;;
    *)
        echo "Running all tests..."
        docker-compose run --rm core-api pytest tests/ -v
        ;;
esac

echo "✅ Tests completed!"
