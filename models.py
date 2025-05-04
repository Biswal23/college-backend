from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class College(Base):
    __tablename__ = "colleges"
    name = Column(String, primary_key=True)
    state = Column(String)
    location = Column(String)
    course_level = Column(String)
    fees = Column(Float)
    min_score = Column(Float)
    max_score = Column(Float)
    rank = Column(Integer, nullable=True)
    branches = relationship("CollegeBranch", back_populates="college")
    reviews = relationship("Review", back_populates="college")

class CollegeBranch(Base):
    __tablename__ = "college_branches"
    id = Column(Integer, primary_key=True)
    college_name = Column(String, ForeignKey("colleges.name"))
    branch = Column(String)
    college = relationship("College", back_populates="branches")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    college_name = Column(String, ForeignKey("colleges.name"))
    review_text = Column(String)
    rating = Column(Float)
    college = relationship("College", back_populates="reviews")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
