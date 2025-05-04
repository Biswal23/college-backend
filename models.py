from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class College(Base):
    __tablename__ = 'colleges'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    location = Column(String, nullable=False)
    course_level = Column(String, nullable=False)
    fees = Column(Float, nullable=False)
    min_score = Column(Float, nullable=False)  # Renamed from cutoff_min
    max_score = Column(Float, nullable=False)  # Renamed from cutoff_max
    rank = Column(Integer, nullable=True)  # Added for rank card
    branches = relationship("CollegeBranch", back_populates="college")
    reviews = relationship("Review", back_populates="college")

class CollegeBranch(Base):
    __tablename__ = 'college_branches'
    id = Column(Integer, primary_key=True)
    college_name = Column(String, ForeignKey('colleges.name'), nullable=False)
    branch = Column(String, nullable=False)
    college = relationship("College", back_populates="branches")

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    college_name = Column(String, ForeignKey('colleges.name'), nullable=False)
    review_text = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    college = relationship("College", back_populates="reviews")
