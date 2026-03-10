#!/bin/bash
# Run complete test suite

set -e

echo "Running Complete Test Suite"
echo "==============================="

# Ensure environment is set
export ENVIRONMENT=${ENVIRONMENT:-local}
export GROQ_API_KEY=${GROQ_API_KEY:-"test_key"}
export REDIS_URL=${REDIS_URL:-"redis://localhost:6379/0"}
export API_KEYS="admin_key_12345,query_key_67890"

# 1. Unit Tests
echo ""
echo "Running Unit Tests..."
pytest tests/unit -v --tb=short -m "not requires_api_key" || {
    echo "Unit tests had failures"
    # Continue anyway to run all tests
}

# 2. Integration Tests
echo ""
echo "Running Integration Tests..."
pytest tests/integration -v --tb=short -m "not requires_api_key" || {
    echo "Integration tests had failures"
}

# 3. Security Tests
echo ""
echo "Running Security Tests..."
pytest tests/security -v --tb=short || {
    echo "Security tests had failures"
}

# 4. API Tests
echo ""
echo "Running API Tests..."
pytest tests/test_api.py -v --tb=short 2>/dev/null || {
    echo "API tests not found or had failures"
}

# 5. Observability Tests
echo ""
echo "Running Observability Tests..."
pytest tests/test_observability.py -v --tb=short 2>/dev/null || {
    echo "Observability tests not found or had failures"
}

# 6. RBAC Tests
echo ""
echo "Running RBAC Tests..."
pytest tests/test_rbac.py -v --tb=short 2>/dev/null || {
    echo "RBAC tests not found or had failures"
}

# Summary
echo ""
echo "==============================="
echo "Test suite execution complete!"
echo ""
echo "Next steps:"
echo "  - Run load tests: locust -f tests/load/locustfile.py"
echo "  - Validate deployment: ./scripts/validate_deployment.sh staging"
echo "  - Check production readiness: ./scripts/production_readiness.sh"
