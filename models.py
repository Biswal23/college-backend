from sqlalchemy import Column, Integer, String, Float
from database import Base

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    state = Column(String, nullable=True)
    location = Column(String, nullable=True)
    course_level = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    fees = Column(Float, nullable=True)
    cutoff_min = Column(Float, nullable=True)
    cutoff_max = Column(Float, nullable=True)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, index=True)
    review_text = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
