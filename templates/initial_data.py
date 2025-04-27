from database import SessionLocal, engine, Base
from models import College, Review

def initialize_database():
    """Create database tables and insert sample data"""
    Base.metadata.create_all(bind=engine)
    add_sample_data()

def add_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(College).count() > 0:
            print("Sample data already exists")
            return

        # Sample colleges
        colleges = [
            College(
                name="University of Technology",
                state="New York",
                location="New York City",
                course_level="UG",
                cutoff=85.5,
                fees=25000.00
            ),
            College(
                name="State College",
                state="California",
                location="San Francisco",
                course_level="PG",
                cutoff=78.0,
                fees=32000.00
            ),
            College(
                name="ABC Engineering",
                state="New York",
                location="Buffalo",
                course_level="UG",
                cutoff=82.0,
                fees=28000.00
            )
        ]

        # Sample reviews
        reviews = [
            Review(
                college_name="University of Technology",
                review_text="Excellent faculty and facilities",
                rating=4.5
            ),
            Review(
                college_name="University of Technology",
                review_text="Great campus life",
                rating=4.0
            ),
            Review(
                college_name="State College",
                review_text="Strong research programs",
                rating=4.2
            )
        ]

        # Add to database
        db.add_all(colleges)
        db.add_all(reviews)
        db.commit()
        print("Sample data added successfully")

    except Exception as e:
        db.rollback()
        print(f"Error adding sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
