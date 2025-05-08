from sqlalchemy import Column, Integer, String, Float
from database import Base

class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String)
    location = Column(String)
    course_level = Column(String)
    branch = Column(String)
    fees = Column(Float)
    cutoff_min = Column(Float)
    cutoff_max = Column(Float)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    college_name = Column(String, nullable=False)
    review_text = Column(String)
    rating = Column(Float)
