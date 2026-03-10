#!/bin/bash
# Validate deployment after release

set -e

ENVIRONMENT=${1:-staging}
BASE_URL=${2:-http://localhost:8000}
API_KEY=${STAGING_API_KEY:-""}

echo "Validating $ENVIRONMENT deployment at $BASE_URL"
echo "=================================================="

# Check API key is provided
if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY not provided"
    echo "Usage: $0 <environment> <base_url>"
    echo "Set STAGING_API_KEY or PROD_API_KEY environment variable"
    exit 1
fi

# 1. Health Checks
echo ""
echo "Testing health endpoints..."

LIVENESS=$(curl -sf "$BASE_URL/health/liveness" || echo "failed")
if [[ "$LIVENESS" == *"OK"* ]] || [[ "$LIVENESS" == *"alive"* ]]; then
    echo "  - Liveness: OK"
else
    echo "  - Liveness: FAILED"
    exit 1
fi

READINESS=$(curl -sf "$BASE_URL/health/readiness" || echo "failed")
if [[ "$READINESS" == *"OK"* ]] || [[ "$READINESS" == *"ready"* ]]; then
    echo "  - Readiness: OK"
else
    echo "  - Readiness: DEGRADED (this may be OK if starting up)"
fi

HEALTH_STATUS=$(curl -sf "$BASE_URL/health/health" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "unknown")
echo "  - Full health check: $HEALTH_STATUS"

# 2. Security Tests
echo ""
echo "Testing security controls..."

# Test unauthorized access
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d '{"question":"test","domain":"tax"}')

if [ "$STATUS" -eq 401 ] || [ "$STATUS" -eq 403 ]; then
    echo "  - Authentication required: OK"
else
    echo "  - Authentication required: FAILED (HTTP $STATUS)"
    exit 1
fi

# Test invalid API key
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: invalid_key" \
    -d '{"question":"test","domain":"tax"}')

if [ "$STATUS" -eq 401 ] || [ "$STATUS" -eq 403 ]; then
    echo "  - Invalid API key rejected: OK"
else
    echo "  - Invalid API key rejected: FAILED (HTTP $STATUS)"
    exit 1
fi

# 3. Functional Tests
echo ""
echo "Testing core functionality..."

# Test query endpoint
QUERY_RESPONSE=$(curl -sf -X POST "$BASE_URL/api/v1/query" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"question":"revenue recognition","domain":"tax","top_k":5}')

if [ -n "$QUERY_RESPONSE" ]; then
    echo "  - Query endpoint: OK"
else
    echo "  - Query endpoint: FAILED (no response)"
    exit 1
fi

# Test retrieval endpoint
RETRIEVE_RESPONSE=$(curl -sf -X POST "$BASE_URL/api/v1/query/retrieve" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"question":"tax deduction","domain":"tax","top_k":5}')

if [ -n "$RETRIEVE_RESPONSE" ]; then
    echo "  - Retrieval endpoint: OK"
else
    echo "  - Retrieval endpoint: FAILED"
    exit 1
fi

# Test document stats
STATS_RESPONSE=$(curl -sf "$BASE_URL/api/v1/documents/stats" \
    -H "X-API-Key: $API_KEY")

if [ -n "$STATS_RESPONSE" ]; then
    echo "  - Document stats: OK"
else
    echo "  - Document stats: FAILED"
    exit 1
fi

# Test domains endpoint
DOMAINS_RESPONSE=$(curl -sf "$BASE_URL/api/v1/documents/domains")

if [ -n "$DOMAINS_RESPONSE" ]; then
    echo "  - Domains endpoint: OK"
else
    echo "  - Domains endpoint: FAILED"
    exit 1
fi

# 4. Performance Tests
echo ""
echo "Testing performance..."

# Measure query latency
START_TIME=$(date +%s%N)
QUERY_RESULT=$(curl -sf -X POST "$BASE_URL/api/v1/query" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"question":"test query","domain":"tax"}' > /dev/null)
END_TIME=$(date +%s%N)

LATENCY_MS=$(( ($END_TIME - $START_TIME) / 1000000 ))

if [ "$LATENCY_MS" -gt 3000 ]; then
    echo "  - Warning: Query latency high (${LATENCY_MS}ms)"
else
    echo "  - Query latency: ${LATENCY_MS}ms"
fi

# 5. Observability Tests
echo ""
echo "Testing observability..."

# Check metrics endpoint
METRICS_RESPONSE=$(curl -sf "$BASE_URL/metrics")
if echo "$METRICS_RESPONSE" | grep -q "python_gc"; then
    echo "  - Prometheus metrics: OK"
else
    echo "  - Prometheus metrics: WARNING (basic metrics only)"
fi

# Check OpenAPI spec
OPENAPI_RESPONSE=$(curl -sf "$BASE_URL/openapi.json")
if [ -n "$OPENAPI_RESPONSE" ]; then
    echo "  - OpenAPI spec: OK"
else
    echo "  - OpenAPI spec: FAILED"
    exit 1
fi

# 6. Rate Limiting Test (if configured)
echo ""
echo "Testing rate limiting..."

RATE_LIMIT_HIT=false
for i in {1..65}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$BASE_URL/api/v1/query" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"question\":\"test $i\",\"domain\":\"tax\"}")

    if [ "$STATUS" -eq 429 ]; then
        RATE_LIMIT_HIT=true
        break
    fi
done

if [ "$RATE_LIMIT_HIT" = true ]; then
    echo "  - Rate limiting: OK"
else
    echo "  - Rate limiting: WARNING (not triggered after 65 requests)"
fi

# Summary
echo ""
echo "=================================================="
echo "Deployment validation complete!"
echo "   Environment: $ENVIRONMENT"
echo "   URL: $BASE_URL"
echo "   All critical tests passed"
echo "=================================================="
