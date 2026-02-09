#!/usr/bin/env python3
"""
Test script for validation engine.
"""
from validation.engine import ValidationEngine

# Test data with various validation issues
test_output = {
    "template": "C_01_00",
    "fields": [
        {
            "row": "010",
            "metric_name": "Common Equity Tier 1 capital",
            "value": 500000000.0,
            "status": "populated"
        },
        {
            "row": "020",
            "metric_name": "Additional Tier 1 capital",
            "value": 100000000.0,
            "status": "populated"
        },
        {
            "row": "030",
            "metric_name": "Tier 1 capital",
            "value": 650000000.0,  # Incorrect: should be 600m (500m + 100m)
            "status": "populated"
        },
        # Missing row 040 (T2) - should trigger mandatory field warning
        {
            "row": "050",
            "metric_name": "Total own funds",
            "value": None,  # Missing - should trigger mandatory field warning
            "status": "missing"
        }
    ],
    "validation_warnings": []
}

def test_validation():
    """Test the validation engine."""
    print("=" * 60)
    print("Testing Validation Engine")
    print("=" * 60)
    
    engine = ValidationEngine()
    warnings = engine.validate(test_output)
    
    print(f"\n✅ Validation complete")
    print(f"📊 Total warnings: {len(warnings)}\n")
    
    if warnings:
        print("⚠️  Validation warnings:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("✅ No validation warnings")

if __name__ == "__main__":
    test_validation()
