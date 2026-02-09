#!/usr/bin/env python3
"""
Script to populate the database with sample regulatory documents using MOCK embeddings.
Use this when OpenAI API quota is exhausted, for testing purposes only.
"""
import sys
from pathlib import Path
import random

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))
import os

from db.schema import SessionLocal, RegulatoryDocument
from db.loader import get_c01_documents
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_embedding(text: str, dimension: int = 1536) -> list:
    """
    Generate a mock embedding vector (random values).
    For testing purposes only - NOT for production use.
    """
    # Use text hash as seed for reproducibility
    random.seed(hash(text))
    return [random.gauss(0, 1) for _ in range(dimension)]


def populate_database_mock():
    """
    Load regulatory documents from JSON and populate database with MOCK embeddings.
    """
    db = SessionLocal()
    
    try:
        # Check if data already loaded
        existing_count = db.query(RegulatoryDocument).count()
        if existing_count > 0:
            logger.warning(f"Database already contains {existing_count} documents.")
            
            # Non-interactive check for CI/CD
            if not sys.stdin.isatty() or os.getenv("SKIP_AUTH") == "true":
                logger.info("Non-interactive mode: Skipping data reload since documents already exist.")
                return
                
            response = input("Clear existing data and reload? (y/n): ")
            if response.lower() != 'y':
                logger.info("Skipping data load.")
                return
            
            # Clear existing data
            db.query(RegulatoryDocument).delete()
            db.commit()
            logger.info("Cleared existing documents.")
        
        # Load documents from JSON
        documents = get_c01_documents()
        
        if not documents:
            logger.error("No documents loaded. Check data file.")
            return
        
        logger.info(f"Loaded {len(documents)} documents from JSON")
        logger.info("⚠️  Generating MOCK embeddings (for testing only)...")
        
        # Create database records with mock embeddings
        db_documents = []
        for doc in documents:
            embedding = generate_mock_embedding(doc['content'])
            db_doc = RegulatoryDocument(
                source=doc['source'],
                template=doc['template'],
                section=doc['section'],
                paragraph_id=doc['paragraph_id'],
                content=doc['content'],
                embedding=embedding
            )
            db_documents.append(db_doc)
        
        # Bulk insert
        db.bulk_save_objects(db_documents)
        db.commit()
        
        logger.info(f"✅ Successfully populated database with {len(db_documents)} documents (MOCK embeddings)")
        logger.warning("⚠️  Note: Using mock embeddings. Semantic search accuracy will be limited.")
        logger.warning("   Add OpenAI API key to use real embeddings.")
        
        # Verify
        final_count = db.query(RegulatoryDocument).count()
        logger.info(f"Total documents in database: {final_count}")
    
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("COREP Assistant - Database Population (MOCK EMBEDDINGS)")
    print("=" * 60)
    populate_database_mock()
