"""
Audit Logging System

Centralized audit logging for tool invocations, enabling compliance tracking,
security monitoring, and audit trails for regulatory requirements.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from pathlib import Path
from enum import Enum

class AuditEventType(Enum):
    """Types of audit events"""
    TOOL_INVOKED = "TOOL_INVOKED"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    TOOL_FAILED = "TOOL_FAILED"
    DISCLAIMER_SHOWN = "DISCLAIMER_SHOWN"
    DATA_ACCESSED = "DATA_ACCESSED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    CACHE_HIT = "CACHE_HIT"
    CACHE_MISS = "CACHE_MISS"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"

class AuditLogger:
    """
    Centralized audit logger for Legal Finance RAG tools.
    
    Features:
    - JSON file-based audit trail (one file per day for easy archival)
    - In-memory cache for fast retrieval
    - Compliance-grade event tracking
    - Sensitive data redaction
    - Searchable audit log interface
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize audit logger
        
        Args:
            log_dir: Directory for audit log files (default: app/logs/audit)
        """
        self.log_dir = Path(log_dir or "app/logs/audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory audit log (limited to recent events for performance)
        self.memory_log: List[Dict[str, Any]] = []
        self.max_memory_events = 1000
        
        # Setup Python logger
        self.logger = logging.getLogger("audit")
        self.setup_logging()
    
    def setup_logging(self):
        """Configure Python logging for audit trail"""
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create audit log handler (daily rotation)
        audit_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(audit_file)
        
        # Format: timestamp|event_type|tool|user|status|details
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(
        self,
        event_type: AuditEventType,
        tool_name: str,
        user_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of audit event
            tool_name: Name of the tool
            user_id: User/session identifier
            parameters: Tool parameters (sanitized)
            result: Tool result summary (redacted if sensitive)
            error: Error message if applicable
            execution_time_ms: Execution duration
            metadata: Additional metadata
        
        Returns:
            Event ID for correlation
        """
        
        event_id = self._generate_event_id()
        timestamp = datetime.now().isoformat()
        
        # Build audit event
        audit_event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type.value,
            "tool": tool_name,
            "user_id": user_id or "anonymous",
            "parameters": self._redact_sensitive_data(parameters or {}),
            "result_summary": self._create_result_summary(result),
            "error": error,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {}
        }
        
        # Add to memory log
        self._add_to_memory_log(audit_event)
        
        # Write to JSON file
        self._write_to_audit_file(audit_event)
        
        # Log through Python logger
        self._log_summarized_event(audit_event)
        
        return event_id
    
    def log_tool_invocation(
        self,
        tool_name: str,
        user_id: Optional[str],
        parameters: Dict[str, Any]
    ) -> str:
        """Log a tool invocation start"""
        return self.log_event(
            event_type=AuditEventType.TOOL_INVOKED,
            tool_name=tool_name,
            user_id=user_id,
            parameters=parameters
        )
    
    def log_tool_success(
        self,
        tool_name: str,
        user_id: Optional[str],
        execution_time_ms: float,
        result: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None
    ) -> str:
        """Log successful tool execution"""
        return self.log_event(
            event_type=AuditEventType.TOOL_COMPLETED,
            tool_name=tool_name,
            user_id=user_id,
            result=result,
            execution_time_ms=execution_time_ms,
            metadata={"event_id": event_id} if event_id else {}
        )
    
    def log_tool_failure(
        self,
        tool_name: str,
        user_id: Optional[str],
        error: str,
        execution_time_ms: float,
        parameters: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None
    ) -> str:
        """Log tool execution failure"""
        return self.log_event(
            event_type=AuditEventType.TOOL_FAILED,
            tool_name=tool_name,
            user_id=user_id,
            parameters=parameters,
            error=error,
            execution_time_ms=execution_time_ms,
            metadata={"event_id": event_id} if event_id else {}
        )
    
    def log_rate_limit_exceeded(
        self,
        tool_name: str,
        user_id: str,
        reason: str,
        current_usage: int,
        limit: int
    ) -> str:
        """Log rate limit exceeded event"""
        return self.log_event(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            tool_name=tool_name,
            user_id=user_id,
            error=f"Rate limit exceeded: {reason}",
            metadata={
                "current_usage": current_usage,
                "limit": limit,
                "reason": reason
            }
        )
    
    def log_validation_failure(
        self,
        tool_name: str,
        user_id: Optional[str],
        validation_rule: str,
        parameters: Dict[str, Any],
        reason: str
    ) -> str:
        """Log validation failure"""
        return self.log_event(
            event_type=AuditEventType.VALIDATION_FAILED,
            tool_name=tool_name,
            user_id=user_id,
            parameters=parameters,
            error=f"Validation failed: {reason}",
            metadata={"validation_rule": validation_rule}
        )
    
    def search_audit_log(
        self,
        tool_name: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search audit log for events matching criteria
        
        Args:
            tool_name: Filter by tool name
            user_id: Filter by user
            event_type: Filter by event type
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum results
        
        Returns:
            List of matching audit events
        """
        
        results = []
        
        # Search memory log first (current/recent events)
        for event in reversed(self.memory_log):
            if len(results) >= limit:
                break
            
            if self._event_matches_criteria(event, tool_name, user_id, event_type, start_date, end_date):
                results.append(event)
        
        return results[:limit]
    
    def get_audit_statistics(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics from audit log"""
        
        events = self.search_audit_log(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        stats = {
            "total_events": len(events),
            "by_event_type": {},
            "by_tool": {},
            "by_user": {},
            "error_rate": 0.0,
            "average_execution_time_ms": 0.0
        }
        
        total_exec_time = 0
        failure_count = 0
        exec_count = 0
        
        for event in events:
            # Count by type
            event_type = event.get("event_type")
            stats["by_event_type"][event_type] = stats["by_event_type"].get(event_type, 0) + 1
            
            # Count by tool
            tool = event.get("tool")
            stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1
            
            # Count by user
            user = event.get("user_id")
            stats["by_user"][user] = stats["by_user"].get(user, 0) + 1
            
            # Track failures
            if event_type == "TOOL_FAILED":
                failure_count += 1
            elif event_type == "TOOL_COMPLETED":
                exec_count += 1
                exec_time = event.get("execution_time_ms", 0)
                total_exec_time += exec_time if exec_time else 0
        
        # Calculate rates
        if exec_count > 0:
            stats["average_execution_time_ms"] = total_exec_time / exec_count
            stats["error_rate"] = failure_count / exec_count if exec_count > 0 else 0
        
        return stats
    
    def generate_compliance_report(
        self,
        report_type: str = "daily",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report from audit trail
        
        Args:
            report_type: 'daily', 'weekly', or 'monthly'
            user_id: Optional filter to specific user
        
        Returns:
            Compliance report
        """
        
        stats = self.get_audit_statistics(user_id=user_id)
        events = self.search_audit_log(user_id=user_id, limit=10000)
        
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "period": self._get_period_label(report_type),
            "summary": stats,
            "critical_events": self._identify_critical_events(events),
            "recommendations": self._generate_recommendations(stats)
        }
        
        return report
    
    def export_audit_log_csv(
        self,
        output_file: str,
        user_id: Optional[str] = None,
        limit: int = 10000
    ) -> str:
        """Export audit log to CSV for external analysis"""
        
        import csv
        
        events = self.search_audit_log(user_id=user_id, limit=limit)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if events:
                fieldnames = events[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(events)
        
        return str(output_path)
    
    @staticmethod
    def _generate_event_id() -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def _redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from logged data"""
        
        sensitive_fields = {
            'password', 'secret', 'token', 'api_key', 'email', 'phone',
            'ssn', 'aadhar', 'pan', 'bank_account', 'credit_card'
        }
        
        redacted = {}
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = value
        
        return redacted
    
    @staticmethod
    def _create_result_summary(result: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Create summary of result for audit log"""
        if not result:
            return {}
        
        summary = {}
        for key in list(result.keys())[:5]:  # First 5 fields only
            value = result[key]
            if isinstance(value, (str, int, float, bool)):
                summary[key] = str(value)
            else:
                summary[key] = type(value).__name__
        
        return summary
    
    def _add_to_memory_log(self, event: Dict[str, Any]):
        """Add event to in-memory log"""
        self.memory_log.append(event)
        
        # Keep memory log size bounded
        if len(self.memory_log) > self.max_memory_events:
            self.memory_log = self.memory_log[-self.max_memory_events:]
    
    def _write_to_audit_file(self, event: Dict[str, Any]):
        """Write event to daily JSON audit file"""
        
        audit_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        try:
            with open(audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write audit event: {e}")
    
    def _log_summarized_event(self, event: Dict[str, Any]):
        """Log event summary through Python logger"""
        summary = (
            f"{event['event_type']} | {event['tool']} | "
            f"{event['user_id']} | {event.get('execution_time_ms', 'N/A')}ms"
        )
        
        if event['error']:
            self.logger.error(summary + f" | ERROR: {event['error']}")
        else:
            self.logger.info(summary)
    
    @staticmethod
    def _event_matches_criteria(
        event: Dict[str, Any],
        tool_name: Optional[str],
        user_id: Optional[str],
        event_type: Optional[AuditEventType],
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> bool:
        """Check if event matches search criteria"""
        
        if tool_name and event.get('tool') != tool_name:
            return False
        
        if user_id and event.get('user_id') != user_id:
            return False
        
        if event_type and event.get('event_type') != event_type.value:
            return False
        
        event_timestamp = event.get('timestamp')
        if start_date and event_timestamp < start_date:
            return False
        
        if end_date and event_timestamp > end_date:
            return False
        
        return True
    
    @staticmethod
    def _identify_critical_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical events for compliance report"""
        
        critical_types = {
            'TOOL_FAILED',
            'RATE_LIMIT_EXCEEDED',
            'UNAUTHORIZED_ACCESS',
            'VALIDATION_FAILED'
        }
        
        return [e for e in events if e.get('event_type') in critical_types][:10]
    
    @staticmethod
    def _generate_recommendations(stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on audit statistics"""
        
        recommendations = []
        
        if stats.get('error_rate', 0) > 0.1:
            recommendations.append("High error rate detected - review tool implementations")
        
        if stats.get('by_event_type', {}).get('RATE_LIMIT_EXCEEDED', 0) > 5:
            recommendations.append("Frequent rate limiting - consider increasing quotas")
        
        if max(stats.get('by_user', {}).values() or [0]) > 1000:
            recommendations.append("High usage by single user - monitor for abuse")
        
        if not recommendations:
            recommendations.append("System operating within expected parameters")
        
        return recommendations
    
    @staticmethod
    def _get_period_label(report_type: str) -> str:
        """Get human-readable period label"""
        now = datetime.now()
        if report_type == "daily":
            return now.strftime('%Y-%m-%d')
        elif report_type == "weekly":
            week_start = now - __import__('datetime').timedelta(days=now.weekday())
            return f"Week of {week_start.strftime('%Y-%m-%d')}"
        elif report_type == "monthly":
            return now.strftime('%B %Y')
        return "Unknown"


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def reset_audit_logger():
    """Reset audit logger (mainly for testing)"""
    global _audit_logger
    _audit_logger = None
