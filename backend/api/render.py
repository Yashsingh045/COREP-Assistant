"""
API endpoint for rendering COREP output as HTML.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from renderer.template import render_corep_html
from llm.schema import COREPOutput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["render"])


@router.post("/render", response_class=HTMLResponse)
async def render_corep_template(corep_output: COREPOutput):
    """
    Render COREP output as HTML table.
    
    Args:
        corep_output: COREPOutput model with populated fields
    
    Returns:
        HTML string with formatted COREP template
    """
    try:
        logger.info(f"Rendering COREP template {corep_output.template}")
        
        # Convert Pydantic model to dict
        output_dict = corep_output.model_dump()
        
        # Render as HTML
        html = render_corep_html(output_dict)
        
        logger.info(f"Successfully rendered HTML for {len(corep_output.fields)} fields")
        return HTMLResponse(content=html)
    
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
