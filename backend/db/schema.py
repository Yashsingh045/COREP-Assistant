"""
Database schema for COREP Assistant.
Uses SQLAlchemy ORM with pgvector extension.
"""
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from config import settings

Base = declarative_base()


class RegulatoryDocument(Base):
    """
    Table storing regulatory text chunks with vector embeddings.
    """
    __tablename__ = "regulatory_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)  # 'PRA_Rulebook' or 'EBA_COREP'
    template = Column(String(20), nullable=False)  # 'C_01_00' for prototype
    section = Column(String(100), nullable=False)
    paragraph_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    
    def __repr__(self):
        return f"<RegulatoryDocument(id={self.id}, source={self.source}, paragraph_id={self.paragraph_id})>"


# Database engine and session
engine = create_engine(settings.database_url, echo=True if settings.environment == "development" else False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """
    Initialize database: create tables and pgvector extension.
    Run this once during setup.
    """
    from sqlalchemy import text
    
    # Create pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def get_db():
    """
    Dependency for FastAPI endpoints to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Run this script to initialize the database
    print("Initializing database...")
    init_db()
