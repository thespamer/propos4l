from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# SQLite database URL
DATABASE_URL = f"sqlite:///{data_dir}/propos4l.db"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    pool_pre_ping=True,  # Check connection before using from pool
    pool_recycle=300,  # Recycle connections every 5 minutes
)

def init_db():
    """Initialize database tables"""
    # Import models to register them with SQLModel
    from app.models.database import (
        Document,
        SemanticBlock,
        Proposal,
        ProposalBlock,
        DocumentProposalLink,
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
