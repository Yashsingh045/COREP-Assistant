"""
API endpoint for COREP analysis using LLM.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from db.schema import get_db
from retrieval.search import hybrid_search
from llm.client import call_llm, format_regulatory_context
from llm.schema import COREPOutput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    """Request model for COREP analysis."""
    question: str = Field(..., description="Natural-language question about COREP reporting", min_length=5)
    scenario: str = Field(..., description="Description of the bank's reporting scenario", min_length=10)
    template: str = Field(default="C_01_00", description="COREP template code")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of regulatory paragraphs to retrieve")


@router.post("/analyze", response_model=COREPOutput)
async def analyze_scenario(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a reporting scenario and populate COREP template fields.
    
    This endpoint:
    1. Retrieves relevant regulatory text based on the question + scenario
    2. Calls GPT-4o-mini to interpret the scenario using retrieved rules
    3. Returns structured JSON output with populated fields and justifications
    
    Args:
        request: AnalyzeRequest with question, scenario, and parameters
        db: Database session
    
    Returns:
        COREPOutput with populated template fields
    """
    try:
        logger.info(f"Analyzing scenario for template {request.template}")
        logger.info(f"Question: {request.question}")
        
        # Step 1: Retrieve relevant regulatory text
        # Combine question and scenario for better retrieval
        query = f"{request.question} {request.scenario}"
        
        retrieved_paragraphs = hybrid_search(
            db=db,
            query=query,
            template=request.template,
            top_k=request.top_k
        )
        
        logger.info(f"Retrieved {len(retrieved_paragraphs)} regulatory paragraphs")
        
        # Step 2: Format regulatory context
        regulatory_context = format_regulatory_context(retrieved_paragraphs)
        
        # Step 3: Call LLM to generate COREP output
        corep_output = call_llm(
            question=request.question,
            scenario=request.scenario,
            regulatory_context=regulatory_context
        )
        
        # Step 4: Run validation engine
        from validation.engine import validate_corep_output
        
        # Convert Pydantic model to dict for validation
        output_dict = corep_output.model_dump()
        validated_output = validate_corep_output(output_dict)
        
        # Convert back to Pydantic model
        corep_output = COREPOutput(**validated_output)
        
        logger.info(f"Successfully generated COREP output with {len(corep_output.fields)} fields")
        logger.info(f"Validation warnings: {len(corep_output.validation_warnings)}")
        return corep_output
    
    except Exception as e:
        logger.error(f"Error analyzing scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))
