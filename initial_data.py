from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import College, Review

def initialize_database(first_init: bool = False):
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Initialize database with sample data if first_init is True
    if first_init:
        db = SessionLocal()
        try:
            # Check if database already has data
            if db.query(College).count() > 0:
                return

            # Sample colleges
            colleges = [
                College(
                    name="Tech College",
                    state="Maharashtra",
                    location="Pune",
                    course_level="BTech",
                    branch="Computer Science",
                    fees=150000.0,
                    cutoff_min=600.0,
                    cutoff_max=800.0
                ),
                College(
                    name="Science College",
                    state="Karnataka",
                    location="Bangalore",
                    course_level="Degree",
                    branch="Science",
                    fees=80000.0,
                    cutoff_min=500.0,
                    cutoff_max=700.0
                ),
                College(
                    name="Engineering College",
                    state="Tamil Nadu",
                    location="Chennai",
                    course_level="BTech",
                    branch="Mechanical Engineering",
                    fees=120000.0,
                    cutoff_min=550.0,
                    cutoff_max=750.0
                ),
                College(
                    name="Commerce Institute",
                    state="Gujarat",
                    location="Ahmedabad",
                    course_level="Degree",
                    branch="Commerce",
                    fees=60000.0,
                    cutoff_min=450.0,
                    cutoff_max=650.0
                ),
                College(
                    name="Polytechnic Institute",
                    state="Uttar Pradesh",
                    location="Lucknow",
                    course_level="Diploma",
                    branch="Civil Engineering",
                    fees=50000.0,
                    cutoff_min=400.0,
                    cutoff_max=600.0
                ),
                College(
                    name="Tech College",
                    state="West Bengal",
                    location="Kolkata",
                    course_level="BTech",
                    branch="Electronics and Telecommunication",
                    fees=140000.0,
                    cutoff_min=580.0,
                    cutoff_max=780.0
                ),
                College(
                    name="Science College",
                    state="Kerala",
                    location="Kochi",
                    course_level="Degree",
                    branch="Arts",
                    fees=70000.0,
                    cutoff_min=480.0,
                    cutoff_max=680.0
                ),
                College(
                    name="Engineering College",
                    state="Andhra Pradesh",
                    location="Hyderabad",
                    course_level="BTech",
                    branch="Civil Engineering",
                    fees=130000.0,
                    cutoff_min=570.0,
                    cutoff_max=770.0
                ),
                College(
                    name="Commerce Institute",
                    state="Rajasthan",
                    location="Jaipur",
                    course_level="Degree",
                    branch="Commerce",
                    fees=65000.0,
                    cutoff_min=460.0,
                    cutoff_max=660.0
                ),
                College(
                    name="Polytechnic Institute",
                    state="Delhi",
                    location="New Delhi",
                    course_level="Diploma",
                    branch="Mechanical Engineering",
                    fees=55000.0,
                    cutoff_min=420.0,
                    cutoff_max=620.0
                ),
            ]

            # Sample reviews
            reviews = [
                Review(
                    college_name="Tech College",
                    review_text="Great faculty and infrastructure!",
                    rating=4.5
                ),
                Review(
                    college_name="Science College",
                    review_text="Good environment for learning.",
                    rating=4.0
                ),
            ]

            # Add data to database
            db.add_all(colleges)
            db.add_all(reviews)
            db.commit()

        finally:
            db.close()
