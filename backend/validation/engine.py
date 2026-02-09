"""
Validation engine for COREP outputs.
Validates field values, checks consistency, and generates warnings.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def validate(self, fields: List[Dict[str, Any]]) -> List[str]:
        """
        Validate fields and return list of warning messages.
        
        Args:
            fields: List of field dictionaries
        
        Returns:
            List of validation warning messages
        """
        raise NotImplementedError


class MandatoryFieldRule(ValidationRule):
    """Validate that mandatory fields are populated."""
    
    def __init__(self, mandatory_rows: List[str]):
        super().__init__(
            "mandatory_fields",
            "Checks that all mandatory COREP rows are populated"
        )
        self.mandatory_rows = set(mandatory_rows)
    
    def validate(self, fields: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        
        # Get populated rows
        populated_rows = {f["row"] for f in fields if f.get("value") is not None}
        
        # Check for missing mandatory fields
        missing = self.mandatory_rows - populated_rows
        if missing:
            warnings.append(
                f"Mandatory fields missing: {', '.join(sorted(missing))}"
            )
        
        return warnings


class NumericRangeRule(ValidationRule):
    """Validate that numeric values are within acceptable ranges."""
    
    def __init__(self):
        super().__init__(
            "numeric_range",
            "Checks that numeric values are within acceptable ranges"
        )
    
    def validate(self, fields: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        
        for field in fields:
            value = field.get("value")
            if value is not None and isinstance(value, (int, float)):
                # Check for negative values where not appropriate
                if value < 0 and field["row"] in ["010", "020", "030", "040", "050"]:
                    warnings.append(
                        f"Row {field['row']} ({field['metric_name']}) has negative value: {value}"
                    )
                
                # Check for unreasonably large values (e.g., > £1 trillion)
                if value > 1_000_000_000_000:
                    warnings.append(
                        f"Row {field['row']} ({field['metric_name']}) has unusually large value: {value}"
                    )
        
        return warnings


class DataTypeRule(ValidationRule):
    """Validate that field values have correct data types."""
    
    def __init__(self):
        super().__init__(
            "data_type",
            "Checks that field values have appropriate data types"
        )
    
    def validate(self, fields: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        
        for field in fields:
            value = field.get("value")
            
            # Skip null values
            if value is None:
                continue
            
            # Capital fields should be numeric
            if field["row"] in ["010", "020", "030", "040", "050"]:
                if not isinstance(value, (int, float)):
                    warnings.append(
                        f"Row {field['row']} ({field['metric_name']}) should be numeric, got {type(value).__name__}"
                    )
        
        return warnings


class ConsistencyRule(ValidationRule):
    """Validate cross-field consistency (e.g., totals match sums)."""
    
    def __init__(self):
        super().__init__(
            "consistency",
            "Checks that calculated totals match sum of components"
        )
    
    def validate(self, fields: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        
        # Create lookup for easy access
        field_map = {f["row"]: f.get("value") for f in fields}
        
        # Check: T1 (030) = CET1 (010) + AT1 (020)
        cet1 = field_map.get("010")
        at1 = field_map.get("020")
        t1 = field_map.get("030")
        
        if all(v is not None for v in [cet1, at1, t1]):
            expected_t1 = cet1 + at1
            if abs(t1 - expected_t1) > 0.01:  # Allow small floating point differences
                warnings.append(
                    f"Tier 1 capital (Row 030: £{t1:,.0f}) does not equal CET1 + AT1 "
                    f"(£{cet1:,.0f} + £{at1:,.0f} = £{expected_t1:,.0f})"
                )
        
        # Check: Total own funds (050) = T1 (030) + T2 (040)
        t2 = field_map.get("040")
        total_own_funds = field_map.get("050")
        
        if all(v is not None for v in [t1, t2, total_own_funds]):
            expected_total = t1 + t2
            if abs(total_own_funds - expected_total) > 0.01:
                warnings.append(
                    f"Total own funds (Row 050: £{total_own_funds:,.0f}) does not equal T1 + T2 "
                    f"(£{t1:,.0f} + £{t2:,.0f} = £{expected_total:,.0f})"
                )
        
        return warnings


class ValidationEngine:
    """Main validation engine that applies all rules."""
    
    def __init__(self):
        # Define validation rules for C 01.00
        self.rules = [
            MandatoryFieldRule(mandatory_rows=["010", "030", "050"]),
            NumericRangeRule(),
            DataTypeRule(),
            ConsistencyRule()
        ]
    
    def validate(self, corep_output: Dict[str, Any]) -> List[str]:
        """
        Run all validation rules on COREP output.
        
        Args:
            corep_output: Dictionary with 'fields' and 'validation_warnings'
        
        Returns:
            List of validation warning messages
        """
        all_warnings = []
        fields = corep_output.get("fields", [])
        
        for rule in self.rules:
            try:
                warnings = rule.validate(fields)
                all_warnings.extend(warnings)
                
                if warnings:
                    logger.info(f"Rule '{rule.name}' found {len(warnings)} warnings")
            
            except Exception as e:
                logger.error(f"Error in validation rule '{rule.name}': {e}")
                all_warnings.append(f"Validation error in {rule.name}: {str(e)}")
        
        return all_warnings


def validate_corep_output(corep_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate COREP output and append validation warnings.
    
    Args:
        corep_output: COREP output dictionary
    
    Returns:
        Updated COREP output with validation warnings
    """
    engine = ValidationEngine()
    validation_warnings = engine.validate(corep_output)
    
    # Merge with existing warnings (if any from LLM)
    existing_warnings = corep_output.get("validation_warnings", [])
    all_warnings = list(set(existing_warnings + validation_warnings))  # Deduplicate
    
    corep_output["validation_warnings"] = all_warnings
    
    logger.info(f"Validation complete: {len(all_warnings)} total warnings")
    return corep_output
