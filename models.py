from sqlalchemy import Column, Integer, String, Float
from database import Base

class College(Base):
    __tablename__ = 'colleges'  # Explicit table name
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    location = Column(String)
    course_level = Column(String)  # 'UG' or 'PG'
    cutoff = Column(Float)
    fees = Column(Float)

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, nullable=False)
    review_text = Column(String)
    rating = Column(Float)
