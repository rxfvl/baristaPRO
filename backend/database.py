import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Fallbacks for local testing if no .env is found (not recommended for production)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "baristadb")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Create the SQLAlchemy engine
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Failed to initialize PostgreSQL engine. Error: {e}")
    # Fallback to sqlite for development/testing if oracle is not available yet
    print("Falling back to local SQLite for backend development.")
    DATABASE_URL = "sqlite:///./backend_fallback.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get a database session for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
