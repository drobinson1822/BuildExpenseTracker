import os
import socket
from urllib.parse import urlparse, urlunparse, quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from typing import Generator, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get and validate the database URL from environment variables"""
    # Get the database URL from environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Parse the URL to check the scheme
    parsed_url = urlparse(database_url)
    
    # In test or development environment, allow SQLite
    if os.getenv("ENV") in ["test", "development"] and database_url.startswith('sqlite://'):
        return database_url
        
    # For production environments, require PostgreSQL
    if parsed_url.scheme != 'postgresql':
        # If it's a postgres:// URL, convert it to postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        else:
            raise ValueError(
                "DATABASE_URL must start with postgresql:// or postgres:// for non-test environments"
            )
    
    return database_url

# Get the database URL
try:
    DATABASE_URL = get_database_url()
    logger.info(f"Using database URL: {DATABASE_URL.split('@')[-1]}")
except Exception as e:
    logger.error(f"Error getting database URL: {e}")
    raise

# Configure SQLAlchemy engine with appropriate settings based on the database type
if DATABASE_URL.startswith('sqlite'):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL configuration with connection pooling
    pg_connect_args = {
        'connect_timeout': 10,  # 10 second connection timeout
        'keepalives': 1,  # Enable keepalive
        'keepalives_idle': 30,  # Seconds before sending keepalive
        'keepalives_interval': 10,  # Interval between keepalive packets
        'keepalives_count': 5,  # Number of keepalive packets to send before considering the connection dead
        'options': '-c statement_timeout=15000'  # 15 second statement timeout
    }
    
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,  # Number of connections to keep open
        max_overflow=10,  # Number of connections to create beyond pool_size when needed
        pool_timeout=30,  # Seconds to wait before giving up on getting a connection
        pool_recycle=1800,  # Recycle connections after 30 minutes
        pool_pre_ping=True,  # Enable connection health checks
        echo=False,  # Set to True for SQL query logging
        connect_args=pg_connect_args
    )

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields database sessions.
    Handles session lifecycle and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
