"""
Input Validation System

Comprehensive input validation to ensure tool parameters are reasonable,
valid, and prevent abuse through unrealistic requests.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import re

class ValidationErrorType(Enum):
    """Types of validation errors"""
    INVALID_TYPE = "invalid_type"
    OUT_OF_RANGE = "out_of_range"
    INVALID_FORMAT = "invalid_format"
    MISSING_REQUIRED = "missing_required"
    INVALID_CHOICE = "invalid_choice"
    BUSINESS_LOGIC_ERROR = "business_logic_error"

@dataclass
class ValidationError:
    """Validation error information"""
    field: str
    error_type: ValidationErrorType
    message: str
    provided_value: Any
    expected_type: Optional[str] = None
    valid_values: Optional[List[Any]] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None

class ValidationRule:
    """Base class for validation rules"""
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        """
        Validate a value
        
        Returns:
            None if valid, ValidationError if invalid
        """
        raise NotImplementedError

class TypeRule(ValidationRule):
    """Validate value type"""
    
    def __init__(self, expected_type: Union[type, Tuple[type, ...]]):
        self.expected_type = expected_type
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None  # Nulls handled by RequiredRule
        
        if not isinstance(value, self.expected_type):
            type_name = self.expected_type.__name__ if hasattr(self.expected_type, '__name__') else str(self.expected_type)
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_TYPE,
                message=f"Expected {type_name}, got {type(value).__name__}",
                provided_value=value,
                expected_type=type_name
            )
        
        return None

class RangeRule(ValidationRule):
    """Validate numeric range"""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, 
                 max_value: Optional[Union[int, float]] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None
        
        if not isinstance(value, (int, float)):
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_TYPE,
                message="Range validation requires numeric value",
                provided_value=value
            )
        
        if self.min_value is not None and value < self.min_value:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.OUT_OF_RANGE,
                message=f"Value {value} is less than minimum {self.min_value}",
                provided_value=value,
                min_value=self.min_value,
                max_value=self.max_value
            )
        
        if self.max_value is not None and value > self.max_value:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.OUT_OF_RANGE,
                message=f"Value {value} is greater than maximum {self.max_value}",
                provided_value=value,
                min_value=self.min_value,
                max_value=self.max_value
            )
        
        return None

class ChoiceRule(ValidationRule):
    """Validate value is in allowed choices"""
    
    def __init__(self, choices: List[Any]):
        self.choices = choices
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None
        
        if value not in self.choices:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_CHOICE,
                message=f"'{value}' is not in valid choices",
                provided_value=value,
                valid_values=self.choices
            )
        
        return None

class DateRangeRule(ValidationRule):
    """Validate date ranges make sense"""
    
    def __init__(self, allow_future: bool = False, max_age_days: Optional[int] = None):
        self.allow_future = allow_future
        self.max_age_days = max_age_days
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None
        
        try:
            if isinstance(value, str):
                parsed_date = datetime.fromisoformat(value).date()
            elif isinstance(value, date):
                parsed_date = value
            else:
                return ValidationError(
                    field=field_name,
                    error_type=ValidationErrorType.INVALID_FORMAT,
                    message="Date must be string (ISO format) or date object",
                    provided_value=value
                )
            
            today = date.today()
            
            # Check if date is in future
            if not self.allow_future and parsed_date > today:
                return ValidationError(
                    field=field_name,
                    error_type=ValidationErrorType.BUSINESS_LOGIC_ERROR,
                    message="Date cannot be in the future",
                    provided_value=str(parsed_date)
                )
            
            # Check if date is too old
            if self.max_age_days:
                age = (today - parsed_date).days
                if age > self.max_age_days:
                    return ValidationError(
                        field=field_name,
                        error_type=ValidationErrorType.OUT_OF_RANGE,
                        message=f"Date is {age} days old, maximum {self.max_age_days} allowed",
                        provided_value=str(parsed_date)
                    )
        
        except (ValueError, AttributeError):
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_FORMAT,
                message="Invalid date format (use ISO format: YYYY-MM-DD)",
                provided_value=str(value)
            )
        
        return None

class PatternRule(ValidationRule):
    """Validate string matches pattern"""
    
    def __init__(self, pattern: str, error_message: str = "Invalid format"):
        self.pattern = pattern
        self.error_message = error_message
        self.compiled = re.compile(pattern)
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None
        
        if not isinstance(value, str):
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_TYPE,
                message="Pattern validation requires string value",
                provided_value=value
            )
        
        if not self.compiled.match(value):
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_FORMAT,
                message=self.error_message,
                provided_value=value
            )
        
        return None

class LengthRule(ValidationRule):
    """Validate string/collection length"""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None:
            return None
        
        try:
            length = len(value)
        except TypeError:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.INVALID_TYPE,
                message="Value must have length (string, list, dict, etc.)",
                provided_value=value
            )
        
        if self.min_length and length < self.min_length:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.OUT_OF_RANGE,
                message=f"Length {length} is less than minimum {self.min_length}",
                provided_value=value,
                min_value=self.min_length,
                max_value=self.max_length
            )
        
        if self.max_length and length > self.max_length:
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.OUT_OF_RANGE,
                message=f"Length {length} is greater than maximum {self.max_length}",
                provided_value=value,
                min_value=self.min_length,
                max_value=self.max_length
            )
        
        return None

class RequiredRule(ValidationRule):
    """Validate required field is present"""
    
    def validate(self, value: Any, field_name: str) -> Optional[ValidationError]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationError(
                field=field_name,
                error_type=ValidationErrorType.MISSING_REQUIRED,
                message="This field is required",
                provided_value=value
            )
        return None

class FieldValidator:
    """Validator for a single field"""
    
    def __init__(self, name: str, required: bool = False):
        self.name = name
        self.required = required
        self.rules: List[ValidationRule] = []
        
        if required:
            self.rules.append(RequiredRule())
    
    def add_rule(self, rule: ValidationRule) -> 'FieldValidator':
        """Add validation rule"""
        self.rules.append(rule)
        return self
    
    def validate(self, value: Any) -> List[ValidationError]:
        """Validate value against all rules"""
        errors = []
        
        for rule in self.rules:
            error = rule.validate(value, self.name)
            if error:
                errors.append(error)
        
        return errors

    def type(self, expected_type: Union[type, Tuple[type, ...]]) -> 'FieldValidator':
        """Add type validation"""
        return self.add_rule(TypeRule(expected_type))
    
    def range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> 'FieldValidator':
        """Add range validation"""
        return self.add_rule(RangeRule(min_value, max_value))
    
    def choices(self, choices: List[Any]) -> 'FieldValidator':
        """Add choice validation"""
        return self.add_rule(ChoiceRule(choices))
    
    def length(self, min_length: Optional[int] = None, max_length: Optional[int] = None) -> 'FieldValidator':
        """Add length validation"""
        return self.add_rule(LengthRule(min_length, max_length))
    
    def pattern(self, pattern: str, message: str = "Invalid format") -> 'FieldValidator':
        """Add pattern validation"""
        return self.add_rule(PatternRule(pattern, message))
    
    def date_range(self, allow_future: bool = False, max_age_days: Optional[int] = None) -> 'FieldValidator':
        """Add date range validation"""
        return self.add_rule(DateRangeRule(allow_future, max_age_days))

class InputValidator:
    """Comprehensive input validator for tool parameters"""
    
    # Pre-defined validators for common parameters
    AMOUNT_VALIDATOR = FieldValidator("amount").type((int, float)).range(min_value=0, max_value=10_000_000_000)
    PERCENTAGE_VALIDATOR = FieldValidator("percentage").type((int, float)).range(min_value=0, max_value=100)
    DATE_VALIDATOR = FieldValidator("date").type(str).pattern(r'^\d{4}-\d{2}-\d{2}$')
    ENTITY_TYPE_VALIDATOR = FieldValidator("entity_type").type(str).choices([
        'sole_proprietor', 'private_limited_company', 'llp', 'partnership'
    ])
    QUERY_VALIDATOR = FieldValidator("query").type(str).length(min_length=3, max_length=1000)
    
    def __init__(self):
        self.fields: Dict[str, FieldValidator] = {}
    
    def add_field(self, field: FieldValidator) -> 'InputValidator':
        """Add field validator"""
        self.fields[field.name] = field
        return self
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate input data
        
        Args:
            data: Input parameters
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        for field_name, validator in self.fields.items():
            value = data.get(field_name)
            field_errors = validator.validate(value)
            errors.extend(field_errors)
        
        return len(errors) == 0, errors
    
    def validate_and_raise(self, data: Dict[str, Any]):
        """Validate and raise exception if invalid"""
        is_valid, errors = self.validate(data)
        
        if not is_valid:
            error_messages = '\n'.join([f"- {e.field}: {e.message}" for e in errors])
            raise ValueError(f"Validation errors:\n{error_messages}")


# Pre-built validators for common tools

def get_financial_ratio_validator() -> InputValidator:
    """Validator for financial ratio calculator"""
    validator = InputValidator()
    
    validator.add_field(FieldValidator("balance_sheet", required=True).type(dict))
    validator.add_field(FieldValidator("income_statement", required=True).type(dict))
    
    return validator

def get_compliance_checker_validator() -> InputValidator:
    """Validator for compliance checker"""
    validator = InputValidator()
    
    validator.add_field(FieldValidator("entity_type", required=True).type(str).choices([
        'sole_proprietor', 'private_limited_company', 'llp', 'partnership'
    ]))
    
    return validator

def get_penalty_calculator_validator() -> InputValidator:
    """Validator for penalty calculator"""
    validator = InputValidator()
    
    validator.add_field(FieldValidator("violation_type", required=True).type(str))
    validator.add_field(FieldValidator("amount", required=True).type((int, float)).range(min_value=0, max_value=10_000_000_000))
    
    return validator

def get_court_case_search_validator() -> InputValidator:
    """Validator for court case search"""
    validator = InputValidator()
    
    validator.add_field(FieldValidator("query", required=True).type(str).length(min_length=3, max_length=500))
    
    return validator
