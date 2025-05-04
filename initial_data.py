from sqlalchemy import create_engine
from database import Base, SessionLocal
from models import College, CollegeBranch, Review

def init_db():
    # Create database tables
    Base.metadata.create_all(bind=create_engine("sqlite:///college_finder.db"))
    
    # Optional: Insert sample data for testing
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(College).count() == 0:
            # Sample college
            college = College(
                name="Sample Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="UG",
                fees=100000.0,
                min_score=500000.0,
                max_score=1000000.0
            )
            db.add(college)
            
            # Sample branch
            branch = CollegeBranch(
                college_name=college.name,
                branch="Computer Science and Engineering"
            )
            db.add(branch)
            
            # Sample review
            review = Review(
                college_name=college.name,
                review_text="Good college with great facilities",
                rating=4.0
            )
            db.add(review)
            
            db.commit()
            print("Sample data inserted successfully.")
        else:
            print("Database already contains data. Skipping sample data insertion.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
