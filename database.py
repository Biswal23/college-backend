from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your database URL
DATABASE_URL = "your_database_url_here"

# Create the SQLAlchemy engine
engine = create_engine "sqlite:///./college.db"

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()
