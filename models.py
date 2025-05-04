from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class College(Base):
    __tablename__ = "colleges"
    
    name = Column(String, primary_key=True)
    state = Column(String, primary_key=True)
    location = Column(String, primary_key=True)
    course_level = Column(String, nullable=False)
    fees = Column(Float, nullable=False)
    min_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    
    branches = relationship("CollegeBranch", back_populates="college")
    reviews = relationship("Review", back_populates="college")

class CollegeBranch(Base):
    __tablename__ = "college_branches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    college_name = Column(String, ForeignKey("colleges.name"), nullable=False)
    branch = Column(String, nullable=False)
    
    college = relationship("College", back_populates="branches")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    college_name = Column(String, ForeignKey("colleges.name"), nullable=False)
    review_text = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    
    college = relationship("College", back_populates="reviews")
