"""
Embeddings generation module using OpenAI API.
"""
from typing import List
import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for given text using OpenAI API.
    
    Args:
        text: Text to embed
    
    Returns:
        List of floats representing the embedding vector (dimension 1536)
    """
    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
            encoding_format="float"
        )
        
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding for text (length: {len(text)} chars)")
        return embedding
    
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
            encoding_format="float"
        )
        
        embeddings = [item.embedding for item in response.data]
        logger.info(f"Generated {len(embeddings)} embeddings in batch")
        return embeddings
    
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise
