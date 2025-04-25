from sqlalchemy import Column, Integer, String, Float
from database import Base

class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    state = Column(String, index=True)
    location = Column(String, index=True)
    course_level = Column(String, index=True)  # "UG" or "PG"
    cutoff = Column(Float)
    fees = Column(Float)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, index=True)
    review_text = Column(String)
    rating = Column(Float)
