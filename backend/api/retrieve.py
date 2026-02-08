"""
API endpoint for regulatory text retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict
import logging

from db.schema import get_db
from retrieval.search import hybrid_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["retrieval"])


class RetrieveRequest(BaseModel):
    """Request model for text retrieval."""
    query: str = Field(..., description="Search query")
    template: str = Field(default="C_01_00", description="COREP template code")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class RetrieveResponse(BaseModel):
    """Response model for text retrieval."""
    query: str
    template: str
    results: List[Dict]
    count: int


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_regulatory_text(
    request: RetrieveRequest,
    db: Session = Depends(get_db)
):
    """
    Retrieve relevant regulatory text based on query.
    
    Uses hybrid search combining keyword matching and semantic similarity.
    
    Args:
        request: RetrieveRequest with query and parameters
        db: Database session
    
    Returns:
        RetrieveResponse with retrieved documents
    """
    try:
        logger.info(f"Retrieving regulatory text for query: {request.query}")
        
        # Perform hybrid search
        results = hybrid_search(
            db=db,
            query=request.query,
            template=request.template,
            top_k=request.top_k
        )
        
        return RetrieveResponse(
            query=request.query,
            template=request.template,
            results=results,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Error retrieving regulatory text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
