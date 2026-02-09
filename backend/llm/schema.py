"""
Pydantic models for COREP output schema.
Specifically designed for C 01.00 (Own Funds) template.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class FieldOutput(BaseModel):
    """Output for a single COREP field."""
    row: str = Field(..., description="COREP row code (e.g., '010', '020')")
    column: str = Field(default="010", description="COREP column code")
    metric_name: str = Field(..., description="Name of the metric (e.g., 'Common Equity Tier 1 capital')")
    value: Optional[float] = Field(None, description="Numeric value in the base currency, or null if missing")
    currency: str = Field(default="GBP", description="Currency code (default GBP for UK banks)")
    status: Literal["populated", "missing", "inconsistent"] = Field(..., description="Field population status")
    justification: str = Field(..., description="Human-readable explanation for the value or status")
    source_paragraphs: List[str] = Field(default_factory=list, description="Regulatory references (e.g., ['CRR Article 26', 'COREP C0100_010'])")


class COREPOutput(BaseModel):
    """Complete COREP template output."""
    template: str = Field(default="C_01_00", description="COREP template code")
    fields: List[FieldOutput] = Field(default_factory=list, description="List of populated fields")
    validation_warnings: List[str] = Field(default_factory=list, description="List of validation warnings or inconsistencies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template": "C_01_00",
                "fields": [
                    {
                        "row": "010",
                        "column": "010",
                        "metric_name": "Common Equity Tier 1 capital",
                        "value": 500000000,
                        "currency": "GBP",
                        "status": "populated",
                        "justification": "Bank has £500m CET1 capital as stated in scenario",
                        "source_paragraphs": ["CRR Article 26", "COREP C0100_010"]
                    }
                ],
                "validation_warnings": []
            }
        }
