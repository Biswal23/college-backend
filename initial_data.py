from sqlalchemy import create_engine
from models import Base, College, Review

from database import SessionLocal, engine, Base


def initialize_database():
    """Create database tables and insert sample college data if empty."""
    db = SessionLocal()
    try:
        # Check if database is empty
        if not db.query(College).first():
            # Add sample colleges
            colleges = [
                College(name="Tech College", state="Maharashtra", location="Mumbai", course_level="PG", fees=150000, cutoff=1200),
                College(name="Science College", state="Tamil Nadu", location="Chennai", course_level="UG", fees=120000, cutoff=800),
                College(name="Business School", state="Karnataka", location="Bangalore", course_level="PG", fees=200000, cutoff=1000),
                College(name="Arts College", state="Delhi", location="New Delhi", course_level="UG", fees=90000, cutoff=750),
                # Add more sample colleges if you want
            ]
            db.add_all(colleges)
            db.commit()
            print("✅ Sample colleges added to database")
        else:
            print("ℹ️ Colleges already exist in database")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        db.close()

def add_sample_reviews():
    """Add sample reviews if there are none."""
    db = SessionLocal()
    try:
        # Check if any reviews exist
        if not db.query(Review).first():
            reviews = [
                Review(college_name="Tech College", review_text="Excellent placement support", rating=4.5),
                Review(college_name="Science College", review_text="Good faculty but needs better labs", rating=3.8),
                Review(college_name="Business School", review_text="Amazing infrastructure and faculty", rating=4.7),
                Review(college_name="Arts College", review_text="Cultural fests are great", rating=4.2),
                # Add more reviews if you want
            ]
            db.add_all(reviews)
            db.commit()
            print("✅ Sample reviews added to database")
        else:
            print("ℹ️ Reviews already exist in database")
    except Exception as e:
        print(f"❌ Error adding sample reviews: {e}")
    finally:
        db.close()

def reset_database():
    """Drop all tables, recreate them, and insert fresh sample data."""
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("🗑️ All tables dropped")

        # Recreate tables and insert fresh data
        Base.metadata.create_all(bind=engine)
        initialize_database()
        add_sample_reviews()
        print("🔄 Database reset and fresh sample data inserted")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    initialize_database()
    # Choose what you want to do:
    # initialize_database()
    # add_sample_reviews()

    #reset_database()  # Reset everything and add fresh data
