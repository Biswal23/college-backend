from database import SessionLocal, engine
from models import College, Review
from sqlalchemy.exc import IntegrityError

def initialize_database():
    """
    Initialize the database with sample college and review data.
    """
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
                cutoff=1200
            ),
            College(
                name="Engineering College Pune",
                state="Maharashtra",
                location="Pune",
                course_level="BTech",
                branch="Mechanical Engineering",
                fees=120000,
                cutoff=1100
            ),
            College(
                name="Science College Bangalore",
                state="Karnataka",
                location="Bangalore",
                course_level="Degree",
                branch="Science",
                fees=80000,
                cutoff=900
            ),
            College(
                name="Commerce Institute Chennai",
                state="Tamil Nadu",
                location="Chennai",
                course_level="Degree",
                branch="Commerce",
                fees=90000,
                cutoff=850
            ),
            College(
                name="Polytechnic Institute Delhi",
                state="Delhi",
                location="New Delhi",
                course_level="Diploma",
                branch="Civil Engineering",
                fees=60000,
                cutoff=700
            ),
            College(
                name="Tech Institute Hyderabad",
                state="Telangana",
                location="Hyderabad",
                course_level="BTech",
                branch="Electronics and Telecommunication",
                fees=140000,
                cutoff=1150
            ),
            College(
                name="Arts College Kolkata",
                state="West Bengal",
                location="Kolkata",
                course_level="Degree",
                branch="Arts",
                fees=70000,
                cutoff=800
            ),
            College(
                name="Engineering Academy Jaipur",
                state="Rajasthan",
                location="Jaipur",
                course_level="BTech",
                branch="Computer Science",
                fees=130000,
                cutoff=1250
            ),
            College(
                name="Diploma College Ahmedabad",
                state="Gujarat",
                location="Ahmedabad",
                course_level="Diploma",
                branch="Mechanical Engineering",
                fees=65000,
                cutoff=750
            ),
            College(
                name="Science Academy Bhopal",
                state="Madhya Pradesh",
                location="Bhopal",
                course_level="Degree",
                branch="Science",
                fees=85000,
                cutoff=950
            ),
        ]

        # Add colleges to database
        for college in colleges:
            db.add(college)

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

        # Commit changes
        db.commit()
        print(f"✅ Database initialized with {len(colleges)} colleges and {len(reviews)} reviews.")

    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error initializing database: {e}")
    finally:
        db.close()
