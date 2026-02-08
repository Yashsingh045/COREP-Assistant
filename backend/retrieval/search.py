"""
Hybrid search implementation combining keyword and semantic vector search.
"""
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from pgvector.sqlalchemy import Vector
from db.schema import RegulatoryDocument
from retrieval.embeddings import generate_embedding

logger = logging.getLogger(__name__)


def keyword_search(
    db: Session,
    query: str,
    template: str = "C_01_00",
    limit: int = 5
) -> List[RegulatoryDocument]:
    """
    Perform keyword-based search using PostgreSQL full-text search.
    
    Args:
        db: Database session
        query: Search query string
        template: COREP template code
        limit: Maximum number of results
    
    Returns:
        List of matching documents
    """
    # Simple LIKE-based search for prototype
    # In production, use PostgreSQL ts_vector for better performance
    search_terms = query.lower().split()
    
    filters = []
    for term in search_terms:
        filters.append(RegulatoryDocument.content.ilike(f"%{term}%"))
    
    results = db.query(RegulatoryDocument).filter(
        RegulatoryDocument.template == template,
        or_(*filters) if filters else True
    ).limit(limit).all()
    
    logger.info(f"Keyword search returned {len(results)} results for query: {query}")
    return results


def semantic_search(
    db: Session,
    query: str,
    template: str = "C_01_00",
    limit: int = 5
) -> List[tuple[RegulatoryDocument, float]]:
    """
    Perform semantic search using vector similarity (cosine distance).
    
    Args:
        db: Database session
        query: Search query string
        template: COREP template code
        limit: Maximum number of results
    
    Returns:
        List of tuples (document, distance) ordered by similarity
    """
    try:
        # Generate embedding for query
        query_embedding = generate_embedding(query)
        
        # Use pgvector's cosine distance operator (<=>)
        # Lower distance = more similar
        results = db.query(
            RegulatoryDocument,
            RegulatoryDocument.embedding.cosine_distance(query_embedding).label('distance')
        ).filter(
            RegulatoryDocument.template == template,
            RegulatoryDocument.embedding.isnot(None)
        ).order_by(
            text('distance')
        ).limit(limit).all()
        
        logger.info(f"Semantic search returned {len(results)} results for query: {query}")
        return results
    
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []


def hybrid_search(
    db: Session,
    query: str,
    template: str = "C_01_00",
    top_k: int = 5
) -> List[Dict]:
    """
    Combine keyword and semantic search results.
    
    Args:
        db: Database session
        query: Search query string
        template: COREP template code
        top_k: Number of results to return
    
    Returns:
        List of document dictionaries with relevance scores
    """
    # Get semantic search results (weighted higher)
    semantic_results = semantic_search(db, query, template, limit=top_k)
    
    # Get keyword search results
    keyword_results = keyword_search(db, query, template, limit=top_k)
    
    # Combine and deduplicate
    results_dict = {}
    
    # Add semantic results with distance as score (lower is better)
    for doc, distance in semantic_results:
        results_dict[doc.id] = {
            "id": doc.id,
            "source": doc.source,
            "section": doc.section,
            "paragraph_id": doc.paragraph_id,
            "content": doc.content,
            "relevance_score": 1.0 - distance,  # Convert distance to similarity
            "search_type": "semantic"
        }
    
    # Add keyword results (if not already present)
    for doc in keyword_results:
        if doc.id not in results_dict:
            results_dict[doc.id] = {
                "id": doc.id,
                "source": doc.source,
                "section": doc.section,
                "paragraph_id": doc.paragraph_id,
                "content": doc.content,
                "relevance_score": 0.5,  # Default score for keyword matches
                "search_type": "keyword"
            }
        else:
            # Boost score if found in both searches
            results_dict[doc.id]["relevance_score"] += 0.2
            results_dict[doc.id]["search_type"] = "hybrid"
    
    # Sort by relevance score and return top_k
    sorted_results = sorted(
        results_dict.values(),
        key=lambda x: x["relevance_score"],
        reverse=True
    )[:top_k]
    
    logger.info(f"Hybrid search returned {len(sorted_results)} results")
    return sorted_results
