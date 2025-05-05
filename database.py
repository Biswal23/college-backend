from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use SQLite for local development
SQLALCHEMY_DATABASE_URL = "sqlite:///college.db"

# For Render deployment with PostgreSQL, uncomment and set the environment variable:
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
