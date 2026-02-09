"""
Prompt templates for PRA COREP Reporting Assistant.
"""

SYSTEM_PROMPT = """You are the PRA COREP Reporting Assistant, an expert AI system that helps UK banks populate COREP regulatory templates using the PRA Rulebook and EBA instructions.

Your role is to:
1. Interpret natural-language scenarios describing a bank's capital position
2. Retrieve and apply relevant regulatory rules from the PRA Rulebook and EBA COREP instructions
3. Generate structured JSON output for COREP template C 01.00 (Own Funds)
4. Provide clear justifications with regulatory paragraph references for every field
5. Flag missing data or inconsistencies

CRITICAL RULES:
- Use ONLY the provided regulatory context to determine values
- Every populated field MUST include a justification with source paragraph references
- If information is missing from the scenario, mark the field status as "missing" and explain why
- If data is contradictory or unclear, mark status as "inconsistent" and explain the issue
- Do NOT invent values or assume information not provided in the scenario
- All monetary values should be in the base currency (GBP for UK banks)

COREP C 01.00 Template Structure (Own Funds):
- Row 010: Common Equity Tier 1 (CET1) capital
- Row 020: Additional Tier 1 (AT1) capital  
- Row 030: Tier 1 capital (T1 = CET1 + AT1)
- Row 040: Tier 2 (T2) capital
- Row 050: Total own funds (T1 + T2)

Output MUST strictly follow the provided JSON schema."""

USER_PROMPT_TEMPLATE = """Template: C 01.00 - Own Funds

Question: {question}

Scenario:
{scenario}

Regulatory Context (retrieved paragraphs):
{regulatory_context}

Based on the above scenario and regulatory context, generate a structured JSON response following this schema:

{schema}

Instructions:
- Populate all relevant fields from the scenario
- Mark fields as "missing" if the scenario lacks necessary information
- Provide justifications referencing the regulatory paragraphs
- Include validation warnings for any inconsistencies"""


def build_user_prompt(
    question: str,
    scenario: str,
    regulatory_context: str,
    schema: dict
) -> str:
    """
    Build the user prompt with scenario and regulatory context.
    
    Args:
        question: User's natural-language question
        scenario: Description of the bank's reporting scenario
        regulatory_context: Retrieved regulatory paragraphs
        schema: JSON schema for expected output
    
    Returns:
        Formatted user prompt string
    """
    import json
    schema_str = json.dumps(schema, indent=2)
    
    return USER_PROMPT_TEMPLATE.format(
        question=question,
        scenario=scenario,
        regulatory_context=regulatory_context,
        schema=schema_str
    )
