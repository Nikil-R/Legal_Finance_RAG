"""
Legal Disclaimer and Compliance Module

Ensures all tool responses include appropriate legal disclaimers,
data freshness warnings, and recommendations to consult professionals.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DisclaimerConfig:
    """Configuration for legal disclaimers"""
    include_disclaimer: bool = True
    include_last_updated: bool = True
    include_professional_recommendation: bool = True
    data_max_age_days: int = 180  # 6 months
    generate_usage_analytics: bool = True

# Global disclaimer configuration
DISCLAIMER_CONFIG = DisclaimerConfig()

# Default legal disclaimer text
DEFAULT_LEGAL_DISCLAIMER = """
⚠️ LEGAL DISCLAIMER:
This information is provided for educational and informational purposes only. 
It is NOT a substitute for professional legal, financial, or tax advice. 
The accuracy and applicability of this information depends on your specific circumstances.

LIMITATIONS:
- Information may be outdated or incomplete
- Laws and regulations change frequently
- No attorney-client relationship is established
- Results should not be relied upon for actual compliance decisions

RECOMMENDATION:
Please consult with qualified professionals (lawyers, accountants, tax advisors) 
before making any business or financial decisions based on this information.
"""

TOOL_SPECIFIC_DISCLAIMERS = {
    "calculate_income_tax": """
This tax calculation is based on assumptions for FY 2026-27 and assumes:
- Standard deductions as per current tax law
- No other income sources beyond specified amount
- Eligibility for Section 80A rebate without disqualifying factors
- Actual tax liability depends on your complete financial profile

Consult a Chartered Accountant for proper tax planning.
""",
    
    "check_compliance": """
This compliance information represents general requirements that may apply 
to your business type. However:
- State/local regulations may impose additional requirements
- Industry-specific regulations not covered
- Requirements change frequently
- Your specific situation may have exceptions

Always verify with regulatory authorities and legal counsel for definitive guidance.
""",
    
    "calculate_financial_ratios": """
These ratios are mathematical calculations based on provided financial data. 
However:
- Accuracy depends entirely on input data accuracy
- Ratios alone cannot provide complete financial picture
- Industry benchmarks vary significantly
- Accounting standards (AS vs Ind-AS) affect interpretation
- Professional financial analysis required for actual decision-making

Have your financial statements audited by qualified professionals.
""",
    
    "calculate_penalties_and_interest": """
Penalty calculations are estimates based on statutory rates. 
However:
- Actual liability depends on specific facts and circumstances
- Penalties may be reduced through appeals/relief applications
- Criminal implications require immediate legal counsel
- Settlement/negotiation options may be available
- This is NOT a legal opinion on liability

Contact a tax lawyer immediately for violation matters.
""",
    
    "search_court_cases": """
Court case information provides legal precedent only. 
However:
- Precedent applicability depends on jurisdiction and facts
- Cases are constantly being overruled or distinguished
- Digital case descriptions may lack nuance from full judgments
- Context and dissenting opinions matter significantly

Consult a lawyer to apply precedents to your situation.
""",
    
    "track_amendments": """
Amendment information reflects current understanding at data collection time. 
However:
- Amendment details may be incomplete
- Transitional provisions are complex
- Interpretation varies by authority
- Implementation dates may change
- Recent amendments may lack enforcement guidance

Discuss amendments with your legal/tax advisor before relying on them.
""",
    
    "compare_documents": """
Document comparison identifies textual differences only. 
However:
- Legal implications of differences require expert analysis
- Deletion of clauses may create ambiguity
- Cross-references may create unintended consequences
- Ambiguous language requires legal interpretation

Have contracts reviewed by a lawyer before execution.
"""
}


class ComplianceManager:
    """Manages legal disclaimers and compliance tracking"""
    
    def __init__(self, config: Optional[DisclaimerConfig] = None):
        self.config = config or DISCLAIMER_CONFIG
        self.audit_log: List[Dict[str, Any]] = []
    
    def add_disclaimer_to_result(
        self,
        result: Dict[str, Any],
        tool_name: str,
        data_last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add legal disclaimers and compliance information to tool result.
        
        Args:
            result: Original tool result
            tool_name: Name of the tool that generated result
            data_last_updated: When the reference data was last updated
        
        Returns:
            Result enhanced with disclaimers and compliance info
        """
        if not self.config.include_disclaimer:
            return result
        
        # Create compliance block
        compliance_info = {
            "disclaimer": DEFAULT_LEGAL_DISCLAIMER,
            "tool_specific_disclaimer": TOOL_SPECIFIC_DISCLAIMERS.get(tool_name, ""),
            "data_info": {}
        }
        
        # Add data freshness information
        if self.config.include_last_updated and data_last_updated:
            last_updated_date = datetime.fromisoformat(data_last_updated)
            age_days = (datetime.now() - last_updated_date).days
            
            compliance_info["data_info"] = {
                "last_updated": data_last_updated,
                "age_days": age_days,
                "is_stale": age_days > self.config.data_max_age_days,
                "staleness_warning": f"⚠️ Data is {age_days} days old" if age_days > 90 else None
            }
            
            if age_days > self.config.data_max_age_days:
                logger.warning(
                    f"Tool {tool_name} using stale data ({age_days} days old). "
                    f"Threshold: {self.config.data_max_age_days} days"
                )
        
        # Add professional recommendation
        if self.config.include_professional_recommendation:
            compliance_info["professional_recommendation"] = (
                "This information should be reviewed by a qualified professional "
                "before making actual business or legal decisions."
            )
        
        # Add to result with new key
        enhanced_result = {
            **result,
            "_compliance": compliance_info
        }
        
        return enhanced_result
    
    def log_tool_invocation(
        self,
        tool_name: str,
        user_id: Optional[str],
        parameters: Dict[str, Any],
        result_success: bool,
        execution_time_ms: float
    ):
        """Log tool invocation for audit trail"""
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "user_id": user_id or "anonymous",
            "parameters": self._sanitize_parameters(parameters),
            "success": result_success,
            "execution_time_ms": execution_time_ms
        }
        
        self.audit_log.append(audit_entry)
        
        if self.config.generate_usage_analytics:
            logger.info(f"Tool invocation: {tool_name} by {user_id} in {execution_time_ms}ms")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit log (for compliance team)"""
        return self.audit_log[-limit:]
    
    def check_data_staleness(
        self,
        tool_name: str,
        data_last_updated: str
    ) -> Dict[str, Any]:
        """Check if tool data is becoming stale"""
        
        last_updated_date = datetime.fromisoformat(data_last_updated)
        age_days = (datetime.now() - last_updated_date).days
        
        return {
            "tool": tool_name,
            "last_updated": data_last_updated,
            "age_days": age_days,
            "status": self._get_staleness_status(age_days),
            "requires_update": age_days > self.config.data_max_age_days,
            "update_urgency": self._calculate_update_urgency(age_days)
        }
    
    @staticmethod
    def _sanitize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from logged parameters"""
        sanitized = {}
        
        # List of potentially sensitive parameter names
        sensitive_fields = ['password', 'secret', 'token', 'api_key', 'email', 'phone']
        
        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def _get_staleness_status(age_days: int) -> str:
        """Determine staleness status based on age"""
        if age_days <= 30:
            return "✅ Current"
        elif age_days <= 90:
            return "⚠️ Aging"
        elif age_days <= 180:
            return "⚠️ Consider Updating"
        else:
            return "🔴 Stale - Requires Update"
    
    @staticmethod
    def _calculate_update_urgency(age_days: int) -> str:
        """Calculate urgency for data update"""
        if age_days <= 30:
            return "low"
        elif age_days <= 90:
            return "medium"
        elif age_days <= 180:
            return "high"
        else:
            return "critical"


class DataFreshnessTracker:
    """Tracks version and freshness of all reference data"""
    
    def __init__(self):
        self.data_versions: Dict[str, Dict[str, Any]] = {
            "court_cases": {
                "version": "1.0",
                "last_updated": "2024-03-12",
                "source": "Sample data - Replace with SCC Online/Manupatra",
                "record_count": 3,
                "status": "sample"
            },
            "compliance_requirements": {
                "version": "1.0",
                "last_updated": "2024-03-12",
                "source": "Sample data - Replace with MCA/State portals",
                "record_count": 6,
                "status": "sample"
            },
            "financial_ratios": {
                "version": "1.0",
                "last_updated": "2024-03-12",
                "source": "Standard definitions",
                "record_count": 20,
                "status": "current"
            },
            "amendments_circulars": {
                "version": "1.0",
                "last_updated": "2024-03-12",
                "source": "Sample data - Replace with CBDT/RBI notifications",
                "record_count": 3,
                "status": "sample"
            },
            "penalties_interest": {
                "version": "1.0",
                "last_updated": "2024-03-12",
                "source": "Sample data - Verify with tax law",
                "record_count": "comprehensive",
                "status": "sample"
            }
        }
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get status of all reference data"""
        return {
            "check_timestamp": datetime.now().isoformat(),
            "data_versions": self.data_versions,
            "action_required": self._identify_required_actions()
        }
    
    def _identify_required_actions(self) -> List[str]:
        """Identify which data needs updating"""
        actions = []
        
        for dataset, info in self.data_versions.items():
            if info["status"] == "sample":
                actions.append(f"Replace {dataset} with real data from official sources")
        
        return actions
    
    def update_version(self, dataset: str, version: str, last_updated: str, source: str):
        """Update version information for a dataset"""
        if dataset in self.data_versions:
            self.data_versions[dataset].update({
                "version": version,
                "last_updated": last_updated,
                "source": source,
                "status": "current"
            })


# Global instances
compliance_manager = ComplianceManager()
freshness_tracker = DataFreshnessTracker()


def get_compliance_manager() -> ComplianceManager:
    """Get global compliance manager instance"""
    return compliance_manager


def get_freshness_tracker() -> DataFreshnessTracker:
    """Get global freshness tracker instance"""
    return freshness_tracker
