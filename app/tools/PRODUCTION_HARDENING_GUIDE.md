"""
Production Hardening Implementation Guide

Complete guide for integrating production-grade safeguards into Legal Finance RAG tools.
"""

# PRODUCTION HARDENING CHECKLIST

## HIGH PRIORITY (WEEK 1)

### 1. Legal Disclaimer Mechanism ✅ IMPLEMENTED

**File**: `app/tools/compliance.py`
**Features**:

- Tool-specific disclaimers with legal language
- Data freshness warnings with age tracking
- Professional consultation recommendations
- Audit-trail compatible logging

**Integration**:

```python
from app.tools.compliance import get_compliance_manager

# In tool executor or at tool response time:
compliance_mgr = get_compliance_manager()
result_with_disclaimer = compliance_mgr.add_disclaimer_to_result(
    result=tool_result,
    tool_name="search_court_cases",
    data_last_updated="2024-03-12"
)
```

**Verification**:

- All tool responses include warnings before deployment
- Disclaimers appear in API responses and UI
- User must acknowledge before using results for actual decisions

---

### 2. Data Freshness Tracking ✅ IMPLEMENTED

**File**: `app/tools/compliance.py` (DataFreshnessTracker class)
**Features**:

- Version tracking for all reference data
- Automatic staleness detection (180-day threshold configurable)
- Migration path from sample to real data
- Update urgency calculation

**Implementation**:

```python
from app.tools.compliance import get_freshness_tracker

# Check data status
tracker = get_freshness_tracker()
status = tracker.get_data_status()

# Update when real data integrated
tracker.update_version(
    dataset="court_cases",
    version="2.0",
    last_updated="2024-03-12",
    source="SCC Online API"
)
```

**Real Data Sources**:

- **Court Cases**: SCC Online (https://www.scconline.com/), Manupatra
- **Compliance Requirements**: MCA (Ministry of Corporate Affairs), State regulatory portals
- **Penalties & Interest**: CBDT (Central Board of Direct Taxation) website
- **Amendments**: RBI, SEBI, CBDT official notifications

---

### 3. Audit Logging System ✅ IMPLEMENTED

**File**: `app/tools/audit_logger.py`
**Features**:

- Comprehensive event logging (invocation, completion, failure)
- Daily rotating audit files (JSON format for parsing)
- Sensitive data redaction
- Compliance reporting and statistics
- CSV export for audits

**Integration**:

```python
from app.tools.audit_logger import get_audit_logger

audit_logger = get_audit_logger()

# Log invocation
event_id = audit_logger.log_tool_invocation(
    tool_name="calculate_penalties_and_interest",
    user_id="user_123",
    parameters={"amount": 50000, "violation_type": "income_tax"}
)

# Log completion
audit_logger.log_tool_success(
    tool_name="calculate_penalties_and_interest",
    user_id="user_123",
    execution_time_ms=145.2,
    event_id=event_id
)

# Generate compliance report
monthly_report = audit_logger.generate_compliance_report(
    report_type="monthly"
)

# Export for external audit
audit_logger.export_audit_log_csv("audit_export_2024_mar.csv")
```

**Compliance**:

- All tool invocations logged for audit trails
- Retention: 7 years per regulatory requirements
- Weekly compliance reports generated automatically

---

## MEDIUM PRIORITY (WEEK 2-3)

### 4. Rate Limiting & Quotas ✅ IMPLEMENTED

**File**: `app/tools/rate_limiter.py`
**Features**:

- Per-user quotas (default: 100/hour)
- Tool-specific limits (expensive: 30-50/hour)
- VIP user support (100x quotas for staff)
- Sliding window quota tracking
- Token bucket implementation for bursty traffic

**Integration**:

```python
from app.tools.rate_limiter import get_rate_limiter
from app.tools.audit_logger import get_audit_logger

limiter = get_rate_limiter()
audit_logger = get_audit_logger()

user_id = "user_123"
tool_name = "document_comparison"

# Check rate limit
allowed, info = limiter.is_allowed(user_id, tool_name, is_vip=False)

if not allowed:
    audit_logger.log_rate_limit_exceeded(
        tool_name=tool_name,
        user_id=user_id,
        reason=info.get('blocked_by'),
        current_usage=info.get('current_usage'),
        limit=info.get('limit')
    )
    raise Exception(f"Rate limit exceeded: {info}")

# Execute tool...

# Get usage summary
usage = limiter.get_usage_summary(user_id, tool_name)
print(f"Usage: {usage['usage_by_window']['per_hour']['current']} / {usage['usage_by_window']['per_hour']['limit']}")
```

**Default Quotas**:

- Standard users: 10/min, 100/hour, 500/day
- Financial ratio calculator: 5/min, 50/hour, 300/day
- Document comparison: 3/min, 30/hour, 200/day
- VIP users: 100/min, 1000/hour, 10000/day

---

### 5. Result Caching Layer ✅ IMPLEMENTED

**File**: `app/tools/cache_layer.py`
**Features**:

- TTL-based caching (configurable per tool)
- LRU eviction (prevents memory bloat)
- Cache statistics and monitoring
- Export/import for persistence
- Search result caching with 1-hour TTL

**Integration**:

```python
from app.tools.cache_layer import get_tool_cache, cached_tool_result

cache = get_tool_cache()

# Option 1: Manual caching
cache_key = cache.get_cache_key("search_court_cases", query="tax evasion")
cached_result = cache.get(cache_key)

if cached_result is None:
    # Execute tool
    result = search_court_cases(query="tax evasion")
    # Cache for 1 hour
    cache.set(cache_key, result, ttl_seconds=3600, tool_name="search_court_cases")
else:
    result = cached_result

# Option 2: Decorator (automatic)
@cached_tool_result(ttl_seconds=86400)  # 24 hours
def calculate_financial_ratios(**kwargs):
    # ... implementation
    pass

# Monitor cache
stats = cache.get_statistics()
print(f"Cache hit rate: {stats['hit_rate']}%")

# Invalidate when data updates
cache.invalidate_by_tool("search_court_cases")  # Clear all court cases
cache.invalidate_pattern("compliance")  # Clear all compliance data
```

**TTL Strategy**:

- Court cases: Never expire (immutable unless overruled)
- Compliance matrices: 30 days (regulations change)
- Calculation results: 24 hours (input-dependent)
- Search results: 1 hour (data may update)

---

### 6. Enhanced Input Validation ✅ IMPLEMENTED

**File**: `app/tools/input_validator.py`
**Features**:

- Type checking, range validation, choice whitelist
- Date validation (no future dates, reasonable age)
- Pattern matching for IDs/codes
- Business logic validation
- Detailed error reporting

**Integration**:

```python
from app.tools.input_validator import (
    InputValidator,
    get_financial_ratio_validator,
    get_compliance_checker_validator
)

# Use pre-built validators
validator = get_financial_ratio_validator()
is_valid, errors = validator.validate({
    "balance_sheet": {...},
    "income_statement": {...}
})

if not is_valid:
    for error in errors:
        print(f"{error.field}: {error.message}")
    raise ValueError("Validation failed")

# Or use manual validator
validator = InputValidator()
validator.add_field(FieldValidator("amount", required=True)
    .type((int, float))
    .range(min_value=0, max_value=10_000_000_000)
)
validator.add_field(FieldValidator("date", required=True)
    .date_range(allow_future=False, max_age_days=365)
)

# Execute with validation
try:
    validator.validate_and_raise(user_input)
    result = execute_tool(user_input)
except ValueError as e:
    log_validation_failure(e)
    return {"error": str(e)}
```

**Validation Rules**:

- Amounts: 0 to ₹10 billion (realistic for most entities)
- Percentages: 0 to 100
- Dates: Past dates only, max 365 days old
- Entity types: Whitelist validation
- Queries: 3-1000 characters

---

## INTEGRATION: Tool Executor with All Safeguards

**File**: `app/tools/executor.py` (UPDATE REQUIRED)

```python
from app.tools.compliance import get_compliance_manager
from app.tools.audit_logger import get_audit_logger
from app.tools.rate_limiter import get_rate_limiter
from app.tools.cache_layer import get_tool_cache
from app.tools.input_validator import InputValidator
import time

class SafeToolExecutor:
    """Tool executor with production safeguards integrated"""

    def __init__(self):
        self.compliance_mgr = get_compliance_manager()
        self.audit_logger = get_audit_logger()
        self.rate_limiter = get_rate_limiter()
        self.cache = get_tool_cache()

    def execute_tool(
        self,
        tool_name: str,
        user_id: str,
        parameters: dict,
        validator: InputValidator = None
    ):
        """Execute tool with all production safeguards"""

        start_time = time.time()
        event_id = None

        try:
            # STEP 1: Input validation
            if validator:
                validator.validate_and_raise(parameters)

            # STEP 2: Rate limiting check
            allowed, quota_info = self.rate_limiter.is_allowed(
                user_id, tool_name, is_vip=False
            )

            if not allowed:
                self.audit_logger.log_rate_limit_exceeded(
                    tool_name=tool_name,
                    user_id=user_id,
                    reason=quota_info.get('blocked_by'),
                    current_usage=quota_info.get('current_usage'),
                    limit=quota_info.get('limit')
                )
                raise Exception(f"Rate limit exceeded. {quota_info}")

            # STEP 3: Log invocation
            event_id = self.audit_logger.log_tool_invocation(
                tool_name=tool_name,
                user_id=user_id,
                parameters=parameters
            )

            # STEP 4: Check cache
            cache_key = self.cache.get_cache_key(tool_name, **parameters)
            cached_result = self.cache.get(cache_key)

            if cached_result is not None:
                self.audit_logger.log_event(
                    event_type="CACHE_HIT",
                    tool_name=tool_name,
                    user_id=user_id,
                    metadata={"event_id": event_id}
                )

                # Add disclaimers to cached result
                return self.compliance_mgr.add_disclaimer_to_result(
                    cached_result,
                    tool_name=tool_name
                )

            # STEP 5: Execute tool
            result = self._execute_actual_tool(tool_name, parameters)

            # STEP 6: Cache result
            self.cache.set(cache_key, result, tool_name=tool_name)

            # STEP 7: Add compliance information
            enhanced_result = self.compliance_mgr.add_disclaimer_to_result(
                result,
                tool_name=tool_name
            )

            # STEP 8: Log success
            exec_time_ms = (time.time() - start_time) * 1000
            self.audit_logger.log_tool_success(
                tool_name=tool_name,
                user_id=user_id,
                execution_time_ms=exec_time_ms,
                result=enhanced_result,
                event_id=event_id
            )

            return enhanced_result

        except Exception as e:
            exec_time_ms = (time.time() - start_time) * 1000
            self.audit_logger.log_tool_failure(
                tool_name=tool_name,
                user_id=user_id,
                error=str(e),
                execution_time_ms=exec_time_ms,
                parameters=parameters,
                event_id=event_id
            )
            raise
```

---

## DEPLOYMENT CHECKLIST

- [ ] Compliance module deployed to production
- [ ] Audit logging enabled with daily rotation
- [ ] Rate limiting enforced for all users
- [ ] Cache layer active (memory usage monitored)
- [ ] Input validation enabled on all tool endpoints
- [ ] Disclaimer text reviewed by legal team
- [ ] All tools tested with production safeguards
- [ ] Compliance reports generated weekly
- [ ] User documentation updated with disclaimers
- [ ] Alert system configured for excess errors
- [ ] Real data integration plan documented
- [ ] Backup/restore procedure established
- [ ] Performance benchmarks established (p95 latency, cache hit rate)

---

## MONITORING & MAINTENANCE

### Daily Tasks

- Review error rates and critical events in audit log
- Check cache hit rate (target: >60% for court cases, >40% for calculations)
- Monitor rate limit violations (should be zero for normal users)

### Weekly Tasks

- Generate compliance report
- Review data staleness warnings
- Analyze tool usage patterns
- Check disk usage (audit logs + cache)

### Monthly Tasks

- Performance review (latency, cache effectiveness)
- Compliance audit (who accessed what, when, why)
- Data freshness assessment and update planning
- Export compliance report to external audit trail

### Quarterly Tasks

- Security review
- Real data integration progress check
- Update quota limits based on usage patterns
- Plan for next enhancement phase

---

## SUCCESS METRICS

**Before Production**:

- ❌ No legal disclaimers
- ❌ No audit trail
- ❌ No rate limiting
- ❌ Raw results only

**After Hardening**:

- ✅ All tools show legal disclaimers
- ✅ Complete audit trail of all invocations
- ✅ Rate limiting prevents abuse
- ✅ 85%+ cache hit rate on repeated queries
- ✅ < 1% validation failures (indicates good input filtering)
- ✅ Monthly compliance reports generated
- ✅ Zero unauthorized access attempts blocked
- ✅ <5 second p95 latency

---

## NEXT STEPS (PHASE 2)

1. **Integrate Real Data** (Q2 2024)
   - Connect to SCC Online API
   - Connect to MCA regulatory databases
   - Implement real-time data sync

2. **Performance Optimization** (Q2 2024)
   - Database indexing for faster searches
   - Redis caching for distributed deployments
   - Query optimization for complex financial calculations

3. **Advanced Analytics** (Q3 2024)
   - ML-based anomaly detection in audit logs
   - User behavior analytics
   - Predictive quota management

4. **Regulatory Compliance** (Q3 2024)
   - GDPR compliance review
   - Data retention policies
   - Encryption at rest and in transit

5. **Scale & HA** (Q4 2024)
   - Multi-region deployment
   - Load balancing
   - Disaster recovery procedures
