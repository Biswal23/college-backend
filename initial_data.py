from database import SessionLocal, engine, Base
from models import College, Review
from sqlalchemy.exc import IntegrityError, OperationalError

def initialize_database():
    """
    Initialize the database with sample college and review data.
    """
    # Recreate tables to ensure schema is up-to-date
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables recreated successfully")
    except Exception as e:
        print(f"❌ Error recreating database tables: {e}")
        return

    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        if db.query(College).count() > 0:
            print("✅ Database already initialized with data.")
            return

        # Sample colleges
        colleges = [
            College(
                name="Tech College Mumbai",
                state="Maharashtra",
                location="Mumbai",
                course_level="BTech",
                branch="Computer Science",
                fees=150000,
                cutoff_min=1200,
                cutoff_max=1800
            ),
            College(
                name="Engineering College Pune",
                state="Maharashtra",
                location="Pune",
                course_level="BTech",
                branch="Mechanical Engineering",
                fees=120000,
                cutoff_min=1100,
                cutoff_max=1800
            ),
            College(
                name="Science College Bangalore",
                state="Karnataka",
                location="Bangalore",
                course_level="Degree",
                branch="Science",
                fees=80000,
                cutoff_min=900,
                cutoff_max=1900
            ),
            College(
                name="Commerce Institute Chennai",
                state="Tamil Nadu",
                location="Chennai",
                course_level="Degree",
                branch="Commerce",
                fees=90000,
                cutoff_min=850,
                cutoff_max=1550
            ),
            College(
                name="Polytechnic Institute Delhi",
                state="Delhi",
                location="New Delhi",
                course_level="Diploma",
                branch="Civil Engineering",
                fees=60000,
                cutoff_min=700,
                cutoff_max=1700
            ),
            College(
                name="Tech Institute Hyderabad",
                state="Telangana",
                location="Hyderabad",
                course_level="BTech",
                branch="Electronics and Telecommunication",
                fees=140000,
                cutoff_min=1150,
                cutoff_max=1950
            ),
            College(
                name="Arts College Kolkata",
                state="West Bengal",
                location="Kolkata",
                course_level="Degree",
                branch="Arts",
                fees=70000,
                cutoff_min=800,
                cutoff_max=1800
            ),
            College(
                name="Engineering Academy Jaipur",
                state="Rajasthan",
                location="Jaipur",
                course_level="BTech",
                branch="Computer Science",
                fees=130000,
                cutoff_min=1250,
                cutoff_max=1950
            ),
            College(
                name="Diploma College Ahmedabad",
                state="Gujarat",
                location="Ahmedabad",
                course_level="Diploma",
                branch="Mechanical Engineering",
                fees=65000,
                cutoff_min=750,
                cutoff_max=1750
            ),
            College(
                name="Science Academy Bhopal",
                state="Madhya Pradesh",
                location="Bhopal",
                course_level="Degree",
                branch="Science",
                fees=85000,
                cutoff_min=950,
                cutoff_max=1950
            ),
        ]

        # Add colleges to database
        for college in colleges:
            db.add(college)
            print(f"Added college: {college.name}")

        # Sample reviews
        reviews = [
            Review(
                college_name="Tech College Mumbai",
                review_text="Great faculty and infrastructure!",
                rating=4.5
            ),
            Review(
                college_name="Tech College Mumbai",
                review_text="Good placement opportunities.",
                rating=4.0
            ),
            Review(
                college_name="Engineering College Pune",
                review_text="Excellent mechanical engineering program.",
                rating=4.2
            ),
            Review(
                college_name="Science College Bangalore",
                review_text="Supportive professors, but limited facilities.",
                rating=3.8
            ),
            Review(
                college_name="Commerce Institute Chennai",
                review_text="Affordable and quality education.",
                rating=4.0
            ),
            Review(
                college_name="Polytechnic Institute Delhi",
                review_text="Practical training is top-notch.",
                rating=4.3
            ),
            Review(
                college_name="Tech Institute Hyderabad",
                review_text="Modern campus with great labs.",
                rating=4.5
            ),
            Review(
                college_name="Arts College Kolkata",
                review_text="Creative environment, but needs better resources.",
                rating=3.7
            ),
            Review(
                college_name="Engineering Academy Jaipur",
                review_text="Strong industry connections.",
                rating=4.4
            ),
            Review(
                college_name="Diploma College Ahmedabad",
                review_text="Good for hands-on learning.",
                rating=4.1
            ),
        ]

        # Add reviews to database
        for review in reviews:
            db.add(review)
            print(f"Added review for: {review.college_name}")

        # Commit changes
        db.commit()
        print(f"✅ Database initialized with {len(colleges)} colleges and {len(reviews)} reviews.")

    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error initializing database: IntegrityError: {e}")
    except OperationalError as e:
        db.rollback()
        print(f"❌ Error initializing database: OperationalError: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error initializing database: {e}")
    finally:
        db.close()
