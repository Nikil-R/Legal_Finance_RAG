import time
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from app.tools.registry import ToolRegistry
from app.tools.compliance import get_compliance_manager
from app.tools.audit_logger import get_audit_logger, AuditEventType
from app.tools.rate_limiter import get_rate_limiter
from app.tools.cache_layer import get_tool_cache

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Safely executes tool calls requested by the LLM.
    
    Includes production safeguards:
    - Rate limiting per user/tool
    - Input validation
    - Result caching
    - Audit logging
    - Legal disclaimers
    - Execution timeout
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.timeout = 10  # 10 seconds timeout per tool execution
        self.compliance_mgr = get_compliance_manager()
        self.audit_logger = get_audit_logger()
        self.rate_limiter = get_rate_limiter()
        self.cache = get_tool_cache()

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: Optional[str] = None,
        is_vip: bool = False
    ) -> Dict[str, Any]:
        """
        Safely execute a tool call with production safeguards.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments/parameters
            user_id: User making the request (for audit and rate limiting)
            is_vip: Whether user has VIP status (higher quotas)
        
        Returns:
            Dict with success status, result, and metadata
        """
        start_time = time.perf_counter()
        user_id = user_id or "anonymous"
        event_id = None
        
        try:
            logger.info("Executing tool: %s by user: %s", tool_name, user_id)
            
            # STEP 1: Rate limiting check
            allowed, quota_info = self.rate_limiter.is_allowed(
                user_id=user_id,
                tool_name=tool_name,
                is_vip=is_vip
            )
            
            if not allowed:
                self.audit_logger.log_rate_limit_exceeded(
                    tool_name=tool_name,
                    user_id=user_id,
                    reason=quota_info.get('blocked_by', 'unknown'),
                    current_usage=quota_info.get('current_usage', 0),
                    limit=quota_info.get('limit', 0)
                )
                
                error_msg = f"Rate limit exceeded: {quota_info.get('blocked_by')}. Resets at {quota_info.get('resets_at')}"
                logger.warning("Rate limit exceeded for user %s on tool %s", user_id, tool_name)
                
                return {
                    "success": False,
                    "tool": tool_name,
                    "error": error_msg,
                    "error_type": "rate_limit_exceeded",
                    "quota_info": quota_info
                }
            
            # STEP 2: Log invocation start
            event_id = self.audit_logger.log_tool_invocation(
                tool_name=tool_name,
                user_id=user_id,
                parameters=arguments
            )
            
            # STEP 3: Check cache
            cache_key = self.cache.get_cache_key(tool_name, **arguments)
            cached_result = self.cache.get(cache_key)
            
            if cached_result is not None:
                logger.info("Cache hit for tool %s", tool_name)
                
                # Log cache hit
                self.audit_logger.log_event(
                    event_type=AuditEventType.CACHE_HIT,
                    tool_name=tool_name,
                    user_id=user_id,
                    metadata={"event_id": event_id}
                )
                
                # Add disclaimers to cached result
                cached_result_with_compliance = self.compliance_mgr.add_disclaimer_to_result(
                    cached_result,
                    tool_name=tool_name
                )
                
                return {
                    "success": True,
                    "tool": tool_name,
                    "result": cached_result_with_compliance,
                    "duration_ms": 0,
                    "cache_hit": True,
                    "audit_event_id": event_id
                }
            
            # STEP 4: Get function from registry
            func = self.registry.get_tool_function(tool_name)
            
            # STEP 5: Execute with timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, **arguments)
                result = future.result(timeout=self.timeout)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # STEP 6: Cache result
            self.cache.set(cache_key, result, tool_name=tool_name)
            
            # STEP 7: Add compliance information
            result_with_compliance = self.compliance_mgr.add_disclaimer_to_result(
                result,
                tool_name=tool_name
            )
            
            # STEP 8: Log success
            self.audit_logger.log_tool_success(
                tool_name=tool_name,
                user_id=user_id,
                execution_time_ms=duration_ms,
                result=result_with_compliance,
                event_id=event_id
            )
            
            logger.info(
                "Tool %s executed successfully by %s in %.2fms",
                tool_name, user_id, duration_ms
            )
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result_with_compliance,
                "duration_ms": duration_ms,
                "cache_hit": False,
                "audit_event_id": event_id
            }
            
        except TimeoutError:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            error_msg = f"Tool execution timed out after {self.timeout}s"
            logger.error("Tool %s timed out for user %s after %ds", tool_name, user_id, self.timeout)
            
            self.audit_logger.log_tool_failure(
                tool_name=tool_name,
                user_id=user_id,
                error=error_msg,
                execution_time_ms=duration_ms,
                parameters=arguments,
                event_id=event_id
            )
            
            return {
                "success": False,
                "tool": tool_name,
                "error": error_msg,
                "error_type": "timeout",
                "duration_ms": duration_ms,
                "audit_event_id": event_id
            }
        
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.exception("Error executing tool %s for user %s", tool_name, user_id)
            
            self.audit_logger.log_tool_failure(
                tool_name=tool_name,
                user_id=user_id,
                error=str(e),
                execution_time_ms=duration_ms,
                parameters=arguments,
                event_id=event_id
            )
            
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "error_type": "execution_error",
                "duration_ms": duration_ms,
                "audit_event_id": event_id
            }
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return self.cache.get_statistics()
    
    def get_user_quota_info(self, user_id: str, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get user quota information"""
        return self.rate_limiter.get_usage_summary(user_id, tool_name)
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance system status"""
        return {
            "data_freshness": self.compliance_mgr.freshness_tracker.get_data_status(),
            "audit_log_size": len(self.audit_logger.memory_log),
            "cache_size": len(self.cache.cache)
        }
