from sqlalchemy import create_engine
from models import Base, College, Review
from database import SessionLocal

def create_database():
    # Create SQLite database file
    engine = create_engine("sqlite:///college.db")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def add_sample_data():
    db = SessionLocal()
    try:
        # Add sample colleges
        colleges = [
            College(
                name="University of Technology",
                state="California",
                location="San Francisco",
                course_level="UG",
                cutoff=85.5,
                fees=25000.00
            ),
            College(
                name="State College",
                state="New York",
                location="Albany",
                course_level="PG",
                cutoff=78.0,
                fees=32000.00
            )
        ]
        
        # Add sample reviews
        reviews = [
            Review(
                college_name="University of Technology",
                review_text="Great facilities and faculty",
                rating=4.5
            ),
            Review(
                college_name="State College",
                review_text="Excellent research opportunities",
                rating=4.0
            )
        ]
        
        db.add_all(colleges)
        db.add_all(reviews)
        db.commit()
        print("Sample data added successfully!")
    except Exception as ex:
        db.rollback()
        print(f"Error adding sample data: {ex}")  # Fixed f-string syntax
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
    add_sample_data()
