"""
Data loader for regulatory documents.
Loads PRA Rulebook and EBA COREP instructions from JSON files.
"""
import json
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def load_regulatory_documents(file_path: str) -> List[Dict]:
    """
    Load regulatory documents from JSON file.
    
    Args:
        file_path: Path to JSON file containing regulatory text
    
    Returns:
        List of document dictionaries
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"Regulatory data file not found: {file_path}")
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data.get('documents', [])
        logger.info(f"Loaded {len(documents)} regulatory documents from {file_path}")
        return documents
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading regulatory documents: {e}")
        return []


def get_c01_documents() -> List[Dict]:
    """
    Load C 01.00 (Own Funds) regulatory documents.
    
    Returns:
        List of document dictionaries for C 01.00 template
    """
    # Path relative to backend directory
    data_path = Path(__file__).parent.parent.parent / "data" / "pra_corep_c01.json"
    return load_regulatory_documents(str(data_path))
