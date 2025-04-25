from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

DATABASE_URL = "sqlite:///./college.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Required for SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
