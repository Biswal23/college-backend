from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    state = Column(String, nullable=False)
    location = Column(String, nullable=False)
    course_level = Column(String, nullable=False)
    fees = Column(Float, nullable=False)
    cutoff_min = Column(Float, nullable=False)  # Represents admission rank (min)
    cutoff_max = Column(Float, nullable=False)  # Represents admission rank (max)

    # Relationship with CollegeBranches
    branches = relationship("CollegeBranch", back_populates="college", cascade="all, delete-orphan")

class CollegeBranch(Base):
    __tablename__ = "college_branches"

    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, ForeignKey("colleges.name"), nullable=False)
    branch = Column(String, nullable=False)

    # Relationship with College
    college = relationship("College", back_populates="branches")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, ForeignKey("colleges.name"), nullable=False)
    review_text = Column(String, nullable=False)
    rating = Column(Float, nullable=False)

    # Relationship with College
    college = relationship("College")
