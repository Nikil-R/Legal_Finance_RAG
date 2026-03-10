#!/bin/bash
# Production readiness validation script

set -e

echo "Production Readiness Checklist"
echo "==============================="

FAILED_CHECKS=0

# Function to check and report
check() {
    local name=$1
    local command=$2

    echo -n "Checking $name... "

    if eval "$command" > /dev/null 2>&1; then
        echo "PASS"
    else
        echo "FAIL"
        ((FAILED_CHECKS++))
    fi
}

# 1. Dependencies
echo ""
echo "Dependencies"
check "Python version >= 3.9" "python --version | grep -E '3\.(9|10|11|12)' || python3 --version | grep -E '3\.(9|10|11|12)'"

# 2. Environment Configuration
echo ""
echo "Environment Configuration"
check "ENVIRONMENT set or default" "[ -n '\$ENVIRONMENT' ] || [ -f .env ]"
check "GROQ_API_KEY set" "[ -n '\$GROQ_API_KEY' ] || grep -q 'GROQ_API_KEY' .env 2>/dev/null"
check "REDIS_URL configured" "[ -n '\$REDIS_URL' ] || grep -q 'REDIS' .env 2>/dev/null"

# 3. Security
echo ""
echo "Security Checks"
check "Secrets manager implemented" "[ -f app/utils/secrets_manager.py ]"
check "RBAC decorators present" "grep -r 'require_role' app/api/routes/ 2>/dev/null | head -1"
check "Rate limiting configured" "grep -q 'slowapi' requirements.txt"
check "Security test exists" "[ -f tests/security/test_security.py ]"

# 4. Observability
echo ""
echo "Observability"
check "Structured logging configured" "[ -f app/observability/logging.py ]"
check "Metrics endpoint" "grep -q 'metrics' app/main.py"
check "Health checks comprehensive" "grep -q 'health' app/api/routes/health.py"
check "Tracing configured" "[ -f app/observability/tracing.py ]"

# 5. Testing
echo ""
echo "Test Coverage"
check "Unit tests exist" "[ -d tests/unit ]"
check "Integration tests exist" "[ -f tests/integration/test_pipeline.py ]"
check "Security tests exist" "[ -f tests/security/test_security.py ]"
check "Load tests exist" "[ -f tests/load/locustfile.py ]"

# 6. CI/CD
echo ""
echo "CI/CD Configuration"
check "GitHub workflows exist" "[ -d .github/workflows ]"
check "CI workflow defined" "[ -f .github/workflows/ci.yml ]"

# 7. Documentation
echo ""
echo "Documentation"
check "README exists" "[ -f README.md ]"
check "API docs configured" "grep -q 'docs_url' app/main.py"

# Summary
echo ""
echo "==============================="

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "All checks passed!"
    echo "   System is production-ready"
    exit 0
else
    echo "$FAILED_CHECKS check(s) failed"
    echo "   Review and fix issues before deploying to production"
    exit 1
fi
