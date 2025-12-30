# ============================================================================
# FILE: backend/database.py
# Database Configuration and Session Management
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variable
#DATABASE_URL = "sqlite:///./healthwatch.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./healthwatch_v2.db"
)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Number of connections to maintain
    max_overflow=20,        # Max overflow connections
    pool_pre_ping=True,     # Verify connections before using
    echo=False              # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base for models
Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    """
    Dependency function to get database session
    Automatically closes session after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization function
def init_db():
    """
    Initialize database tables
    Call this to create all tables defined in models
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


# Database reset function (use carefully!)
def reset_db():
    """
    Drop all tables and recreate them
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️ Database reset completed - all data deleted")


if __name__ == "__main__":
    # For testing: python database.py
    init_db()