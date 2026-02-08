#!/usr/bin/env python3
"""
Script to populate the database with sample regulatory documents.
Loads documents from JSON file and generates embeddings.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from db.schema import SessionLocal, RegulatoryDocument
from db.loader import get_c01_documents
from retrieval.embeddings import generate_embeddings_batch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_database():
    """
    Load regulatory documents from JSON and populate database with embeddings.
    """
    db = SessionLocal()
    
    try:
        # Check if data already loaded
        existing_count = db.query(RegulatoryDocument).count()
        if existing_count > 0:
            logger.warning(f"Database already contains {existing_count} documents.")
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
        
        # Extract content for batch embedding generation
        contents = [doc['content'] for doc in documents]
        
        logger.info("Generating embeddings (this may take a moment)...")
        embeddings = generate_embeddings_batch(contents)
        
        # Create database records
        db_documents = []
        for doc, embedding in zip(documents, embeddings):
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
        
        logger.info(f"✅ Successfully populated database with {len(db_documents)} documents")
        
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
    print("COREP Assistant - Database Population")
    print("=" * 60)
    populate_database()
