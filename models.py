from sqlalchemy import Column, Integer, String, Float
from database import Base


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String)
    location = Column(String)
    course_level = Column(String)
    branch = Column(String)
    fees = Column(Float)
    cutoff_min = Column(Integer)  # Ensure this exists
    cutoff_max = Column(Integer)  # Ensure this exists
    
    
class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    college_name = Column(String, nullable=False)  # Links to College.name
    review_text = Column(String)
    rating = Column(Float)
