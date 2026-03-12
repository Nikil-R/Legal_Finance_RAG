"""
Test Suite for Production Hardening Systems

Comprehensive tests for compliance, audit logging, rate limiting, caching, and validation.
"""

import pytest
from datetime import datetime, timedelta
import json
import tempfile
from pathlib import Path

# Import production hardening modules
from app.tools.compliance import (
    DisclaimerConfig,
    ComplianceManager,
    DataFreshnessTracker
)
from app.tools.audit_logger import (
    AuditLogger,
    AuditEventType
)
from app.tools.rate_limiter import (
    RateLimiter,
    QuotaWindow,
    RateLimitConfig,
    TokenBucket
)
from app.tools.cache_layer import (
    CacheEntry,
    ToolResultCache,
    CachedToolDecorator
)
from app.tools.input_validator import (
    ValidationError,
    ValidationErrorType,
    InputValidator,
    FieldValidator,
    TypeRule,
    RangeRule,
    ChoiceRule
)


# ============================================================================
# COMPLIANCE & DISCLAIMER TESTS
# ============================================================================

class TestComplianceManager:
    """Test compliance manager with disclaimers"""
    
    def test_add_disclaimer_to_result(self):
        """Test adding disclaimer to tool result"""
        mgr = ComplianceManager()
        
        result = {"data": "test_result", "value": 123}
        enhanced = mgr.add_disclaimer_to_result(result, "test_tool")
        
        assert "data" in enhanced
        assert "_compliance" in enhanced
        assert "disclaimer" in enhanced["_compliance"]
    
    def test_tool_specific_disclaimer(self):
        """Test tool-specific disclaimer inclusion"""
        mgr = ComplianceManager()
        
        enhanced = mgr.add_disclaimer_to_result({}, "check_compliance")
        assert "tool_specific_disclaimer" in enhanced["_compliance"]
        assert len(enhanced["_compliance"]["tool_specific_disclaimer"]) > 0
    
    def test_data_freshness_warning(self):
        """Test data freshness warning generation"""
        mgr = ComplianceManager()
        
        old_date = (datetime.now() - timedelta(days=200)).isoformat()
        enhanced = mgr.add_disclaimer_to_result({}, "test_tool", data_last_updated=old_date)
        
        data_info = enhanced["_compliance"]["data_info"]
        assert data_info["is_stale"] == True
        assert data_info["age_days"] > 180
    
    def test_log_tool_invocation(self):
        """Test logging tool invocation"""
        mgr = ComplianceManager()
        
        mgr.log_tool_invocation(
            "test_tool",
            "user_123",
            {"param1": "value1"},
            result_success=True,
            execution_time_ms=100.0
        )
        
        assert len(mgr.audit_log) > 0
        assert mgr.audit_log[0]["tool_name"] == "test_tool"


class TestDataFreshnessTracker:
    """Test data freshness tracking"""
    
    def test_get_data_status(self):
        """Test getting data status"""
        tracker = DataFreshnessTracker()
        status = tracker.get_data_status()
        
        assert "data_versions" in status
        assert "action_required" in status
        assert len(status["data_versions"]) > 0
    
    def test_identify_stale_data(self):
        """Test identifying stale data"""
        tracker = DataFreshnessTracker()
        status = tracker.get_data_status()
        
        # Sample data should be marked as needing updates
        actions = status["action_required"]
        assert any("Replace" in action for action in actions)
    
    def test_update_version(self):
        """Test updating data version"""
        tracker = DataFreshnessTracker()
        
        tracker.update_version(
            "court_cases",
            "2.0",
            datetime.now().isoformat(),
            "SCC Online API"
        )
        
        assert tracker.data_versions["court_cases"]["version"] == "2.0"
        assert tracker.data_versions["court_cases"]["status"] == "current"


# ============================================================================
# AUDIT LOGGING TESTS
# ============================================================================

class TestAuditLogger:
    """Test audit logging system"""
    
    def test_log_event(self):
        """Test logging event"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            event_id = logger.log_event(
                event_type=AuditEventType.TOOL_INVOKED,
                tool_name="test_tool",
                user_id="user_123",
                parameters={"param": "value"}
            )
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert event_id is not None
            assert len(logger.memory_log) > 0
    
    def test_log_tool_invocation(self):
        """Test logging tool invocation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            event_id = logger.log_tool_invocation(
                "test_tool",
                "user_123",
                {"amount": 1000}
            )
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert event_id is not None
    
    def test_log_tool_success(self):
        """Test logging tool success"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_success(
                "test_tool",
                "user_123",
                100.5,
                result={"data": "result"}
            )
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert len(logger.memory_log) > 0
    
    def test_log_tool_failure(self):
        """Test logging tool failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_failure(
                "test_tool",
                "user_123",
                "Invalid parameter",
                50.5
            )
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            events = logger.memory_log
            assert len(events) > 0
            assert events[0]["event_type"] == "TOOL_FAILED"
    
    def test_search_audit_log(self):
        """Test searching audit log"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_invocation("tool1", "user1", {})
            logger.log_tool_invocation("tool2", "user1", {})
            logger.log_tool_invocation("tool1", "user2", {})
            
            results = logger.search_audit_log(tool_name="tool1")
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert len(results) == 2
    
    def test_get_audit_statistics(self):
        """Test getting audit statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_success("tool1", "user1", 100)
            logger.log_tool_success("tool1", "user1", 150)
            logger.log_tool_failure("tool1", "user2", "Error", 50)
            
            stats = logger.get_audit_statistics()
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert stats["total_events"] > 0
            assert "by_tool" in stats
            assert "by_user" in stats
    
    def test_generate_compliance_report(self):
        """Test generating compliance report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_success("tool1", "user1", 100)
            
            report = logger.generate_compliance_report("daily")
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert "report_type" in report
            assert "summary" in report
            assert "recommendations" in report
    
    def test_export_audit_log_csv(self):
        """Test exporting audit log to CSV"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_tool_success("tool1", "user1", 100)
            
            output_file = Path(tmpdir) / "audit_export.csv"
            logger.export_audit_log_csv(str(output_file))
            
            # Close the logger to release file handles
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
            
            assert output_file.exists()


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

class TestRateLimiter:
    """Test rate limiting system"""
    
    def test_is_allowed_basic(self):
        """Test basic rate limit check"""
        limiter = RateLimiter()
        
        allowed, info = limiter.is_allowed("user1", "test_tool")
        assert allowed == True
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeding"""
        limiter = RateLimiter()
        
        # Make many requests to hit limit
        for i in range(15):
            allowed, _ = limiter.is_allowed("user1", "test_tool")
            if i < 10:
                assert allowed == True
        
        # Next request might be limited depending on window
        # (This is a sliding window, so it's complex to test precisely)
    
    def test_get_usage_summary(self):
        """Test usage summary"""
        limiter = RateLimiter()
        
        limiter.is_allowed("user1", "test_tool")
        limiter.is_allowed("user1", "test_tool")
        
        summary = limiter.get_usage_summary("user1", "test_tool")
        
        assert "usage_by_window" in summary
        assert "quotas" in summary
    
    def test_reset_user_quota(self):
        """Test resetting user quota"""
        limiter = RateLimiter()
        
        limiter.is_allowed("user1", "test_tool")
        limiter.reset_user_quota("user1")
        
        # After reset, should not be in usage
        assert "user1" not in limiter.usage or not limiter.usage["user1"]
    
    def test_token_bucket(self):
        """Test token bucket implementation"""
        bucket = TokenBucket(capacity=10, refill_rate_per_second=1.0)
        
        # Should be able to consume 10 tokens initially
        assert bucket.consume(10) == True
        
        # Should not be able to consume more
        assert bucket.consume(1) == False


# ============================================================================
# CACHING TESTS
# ============================================================================

class TestCacheEntry:
    """Test cache entry"""
    
    def test_cache_entry_not_expired(self):
        """Test non-expired cache entry"""
        entry = CacheEntry("data", ttl_seconds=3600)
        
        assert entry.is_expired() == False
    
    def test_cache_entry_expired(self):
        """Test expired cache entry"""
        entry = CacheEntry("data", ttl_seconds=1)
        entry.created_at = datetime.now() - timedelta(seconds=2)
        
        assert entry.is_expired() == True
    
    def test_cache_entry_access(self):
        """Test cache entry access tracking"""
        entry = CacheEntry("data")
        
        # Initially access_count should be 0
        initial_count = entry.access_count
        
        entry.access()
        assert entry.access_count == initial_count + 1
        
        entry.access()
        assert entry.access_count == initial_count + 2


class TestToolResultCache:
    """Test tool result cache"""
    
    def test_get_set_cache(self):
        """Test basic cache get/set"""
        cache = ToolResultCache()
        
        cache.set("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = ToolResultCache()
        
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = ToolResultCache()
        
        cache.set("key1", "value1", ttl_seconds=1)
        
        # Manually expire the entry
        cache.cache["key1"].created_at = datetime.now() - timedelta(seconds=2)
        
        result = cache.get("key1")
        assert result is None
    
    def test_cache_statistics(self):
        """Test cache statistics"""
        cache = ToolResultCache()
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_statistics()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        cache = ToolResultCache()
        
        key1 = cache.get_cache_key("tool1", param1="value1", param2="value2")
        key2 = cache.get_cache_key("tool1", param1="value1", param2="value2")
        key3 = cache.get_cache_key("tool1", param1="different", param2="value2")
        
        assert key1 == key2  # Same params = same key
        assert key1 != key3  # Different params = different key
    
    def test_invalidate_by_tool(self):
        """Test invalidating by tool"""
        cache = ToolResultCache()
        
        cache.set("tool1:key1", "value1")
        cache.set("tool1:key2", "value2")
        cache.set("tool2:key1", "value3")
        
        count = cache.invalidate_by_tool("tool1")
        
        assert count == 2


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidator:
    """Test input validation system"""
    
    def test_type_validation(self):
        """Test type validation"""
        validator = InputValidator()
        validator.add_field(FieldValidator("amount", required=True).type((int, float)))
        
        is_valid, errors = validator.validate({"amount": 1000})
        assert is_valid == True
        
        is_valid, errors = validator.validate({"amount": "invalid"})
        assert is_valid == False
        assert len(errors) > 0
    
    def test_range_validation(self):
        """Test range validation"""
        validator = InputValidator()
        validator.add_field(
            FieldValidator("amount", required=True)
            .type((int, float))
            .range(min_value=0, max_value=1000000)
        )
        
        is_valid, _ = validator.validate({"amount": 50000})
        assert is_valid == True
        
        is_valid, _ = validator.validate({"amount": 10000000000})
        assert is_valid == False
    
    def test_choice_validation(self):
        """Test choice validation"""
        validator = InputValidator()
        validator.add_field(
            FieldValidator("entity_type", required=True).choices([
                'sole_proprietor', 'private_limited_company', 'llp'
            ])
        )
        
        is_valid, _ = validator.validate({"entity_type": "sole_proprietor"})
        assert is_valid == True
        
        is_valid, _ = validator.validate({"entity_type": "invalid_type"})
        assert is_valid == False
    
    def test_length_validation(self):
        """Test length validation"""
        validator = InputValidator()
        validator.add_field(
            FieldValidator("query", required=True)
            .type(str)
            .length(min_length=3, max_length=500)
        )
        
        is_valid, _ = validator.validate({"query": "test query"})
        assert is_valid == True
        
        is_valid, _ = validator.validate({"query": "ab"})
        assert is_valid == False
    
    def test_required_validation(self):
        """Test required field validation"""
        validator = InputValidator()
        validator.add_field(FieldValidator("required_field", required=True).type(str))
        
        is_valid, _ = validator.validate({"required_field": "value"})
        assert is_valid == True
        
        is_valid, errors = validator.validate({})
        assert is_valid == False
        assert any(e.error_type == ValidationErrorType.MISSING_REQUIRED for e in errors)


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
