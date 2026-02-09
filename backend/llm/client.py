"""
OpenAI client wrapper for LLM interactions.
"""
from typing import Dict, Any
import json
import logging
from openai import OpenAI
from config import settings
from llm.prompts import SYSTEM_PROMPT, build_user_prompt
from llm.schema import COREPOutput

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


def call_llm(
    question: str,
    scenario: str,
    regulatory_context: str,
    temperature: float = 0.1
) -> COREPOutput:
    """
    Call GPT-4o-mini to analyze scenario and generate COREP output.
    
    Args:
        question: User's natural-language question
        scenario: Bank's reporting scenario description
        regulatory_context: Retrieved regulatory paragraphs (formatted string)
        temperature: LLM temperature (lower = more deterministic)
    
    Returns:
        COREPOutput model with populated fields
    
    Raises:
        Exception: If LLM call fails or output validation fails
    """
    try:
        # Get JSON schema for the prompt
        schema = COREPOutput.model_json_schema()
        
        # Build user prompt
        user_prompt = build_user_prompt(
            question=question,
            scenario=scenario,
            regulatory_context=regulatory_context,
            schema=schema
        )
        
        logger.info(f"Calling LLM with model: {settings.openai_model}")
        
        # Call OpenAI API with JSON mode
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        content = response.choices[0].message.content
        logger.debug(f"LLM response: {content}")
        
        # Parse JSON and validate with Pydantic
        response_data = json.loads(content)
        corep_output = COREPOutput(**response_data)
        
        logger.info(f"Successfully generated COREP output with {len(corep_output.fields)} fields")
        return corep_output
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        raise Exception(f"Invalid JSON response from LLM: {e}")
    
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise


def format_regulatory_context(paragraphs: list[Dict[str, Any]]) -> str:
    """
    Format retrieved regulatory paragraphs into a readable string.
    
    Args:
        paragraphs: List of retrieved paragraph dictionaries
    
    Returns:
        Formatted string with all paragraphs
    """
    if not paragraphs:
        return "No regulatory context retrieved."
    
    formatted = []
    for i, para in enumerate(paragraphs, 1):
        formatted.append(
            f"{i}. [{para['source']}] {para['section']} ({para['paragraph_id']})\n"
            f"   {para['content']}\n"
        )
    
    return "\n".join(formatted)
