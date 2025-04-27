from database import SessionLocal
from models import College, Review
from sqlalchemy import inspect

def initialize_database():
  db = SessionLocal()
  try:
      # Drop existing tables (for testing, remove this in production)
      from database import Base, engine
      Base.metadata.drop_all(bind=engine)
      Base.metadata.create_all(bind=engine)
      print("Dropped and recreated tables for testing.")

      # Check if the College table is empty
      if not db.query(College).first():
          print("Database is empty, adding sample data...")

          # Sample colleges
          colleges = [
              College(
                  name="Tech College",
                  state="Maharashtra",
                  location="Mumbai",
                  course_level="PG",
                  fees=150000,
                  cutoff=1200
              ),
              College(
                  name="Science College",
                  state="Tamil Nadu",
                  location="Chennai",
                  course_level="UG",
                  fees=120000,
                  cutoff=800
              ),
              College(
                  name="Engineering College",
                  state="Karnataka",
                  location="Bangalore",
                  course_level="PG",
                  fees=200000,
                  cutoff=1500
              ),
          ]
          db.add_all(colleges)
          db.commit()
          print("✅ Sample colleges added to college.db")

          # Sample reviews
          reviews = [
              Review(
                  college_name="Tech College",
                  review_text="Great faculty!",
                  rating=4
              ),
              Review(
                  college_name="Science College",
                  review_text="Excellent campus!",
                  rating=5
              ),
          ]
          db.add_all(reviews)
          db.commit()
          print("✅ Sample reviews added to college.db")
      else:
          print("Database already contains data, skipping initialization.")
  except Exception as e:
      print(f"❌ Error initializing database: {e}")
  finally:
      db.close()

if __name__ == "__main__":
  initialize_database()
