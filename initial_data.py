from database import SessionLocal
from models import College, CollegeBranch, Review
import pandas as pd
from io import BytesIO
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database with sample data."""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(College).count() > 0:
            logger.info("Database already initialized, skipping sample data insertion.")
            return

        # Sample college data
        colleges = [
            {
                "name": "Tech College",
                "state": "Maharashtra",
                "location": "Pune",
                "course_level": "BTech",
                "fees": 120000.0,
                "cutoff_min": 600.0,
                "cutoff_max": 800.0
            },
            {
                "name": "Science College",
                "state": "Karnataka",
                "location": "Bangalore",
                "course_level": "Degree",
                "fees": 80000.0,
                "cutoff_min": 500.0,
                "cutoff_max": 700.0
            },
            {
                "name": "Polytechnic Institute",
                "state": "Delhi",
                "location": "New Delhi",
                "course_level": "Diploma",
                "fees": 60000.0,
                "cutoff_min": 400.0,
                "cutoff_max": 600.0
            }
        ]

        # Sample branch data
        branches = [
            {"college_name": "Tech College", "branch": "Computer Science"},
            {"college_name": "Tech College", "branch": "Mechanical Engineering"},
            {"college_name": "Science College", "branch": "Science"},
            {"college_name": "Polytechnic Institute", "branch": "Mechanical Engineering"}
        ]

        # Insert colleges
        for college_data in colleges:
            college = College(**college_data)
            db.add(college)

        # Insert branches
        for branch_data in branches:
            branch = CollegeBranch(**branch_data)
            db.add(branch)
        
        # Sample review data
        reviews = [
            {
                "college_name": "Tech College",
                "review_text": "Great faculty and campus!",
                "rating": 4.5
            },
            {
                "college_name": "Science College",
                "review_text": "Excellent research facilities.",
                "rating": 4.0
            }
        ]

        # Insert reviews
        for review_data in reviews:
            review = Review(**review_data)
            db.add(review)

        db.commit()
        logger.info("✅ Database initialized with sample data successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error initializing database with sample data: {e}")
        raise
    finally:
        db.close()

def process_excel_file(file_content: bytes) -> dict:
    """
    Process an Excel file, convert to JSON, and update the database.
    Supports multiple branches in separate columns or delimited string.
    Stores branches in the CollegeBranch table.
    Returns a JSON representation of the processed data.
    Note: cutoff_min and cutoff_max are rank-based (e.g., admission ranks).
    """
    db = SessionLocal()
    try:
        # Read Excel file into a DataFrame
        df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
        logger.info(f"Excel file read successfully. Columns: {list(df.columns)}")

        # Normalize column names (handle case sensitivity)
        df.columns = [col.strip().lower() for col in df.columns]
        df = df.rename(columns={'name': 'name', 'course level': 'course_level'})

        # Validate required columns for Colleges
        required_columns = [
            'name', 'location', 'course_level', 'fees', 'cutoff_min', 'cutoff_max'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Handle missing 'state' by assuming 'Odisha'
        if 'state' not in df.columns:
            logger.warning("State column missing. Assuming 'Odisha' for all colleges.")
            df['state'] = 'Odisha'

        # Identify branch columns
        branch_columns = [col for col in df.columns if col.startswith('branch') or col == 'branch']
        if not branch_columns:
            raise ValueError("At least one branch column (e.g., 'branch', 'branch1') is required")

        # Validate optional review columns
        review_columns = ['college_name', 'review_text', 'rating']
        has_reviews = all(col in df.columns for col in review_columns)

        # Normalize and validate data
        df = df.dropna(how='all')  # Remove completely empty rows
        colleges_data = []
        branches_data = []
        reviews_data = []

        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        # Expanded allowed branches to accommodate file data
        allowed_branches = {
            "BTech": [
                "Mechanical Engineering", "Computer Science", "Civil Engineering", 
                "Electronics and Telecommunication", "Electrical Engineering",
                "Computer Science and Engineering", "Chemical Engineering",
                "Metallurgical and Materials Engineering", "Production Engineering",
                "Electrical and Electronics Engineering", "Information Technology",
                "Electronics & Communication Engineering", "Textile Engineering",
                "Bio Technology", "Fashion & Apparel Technology", 
                "Electronics & Instrumentation Engineering", "Plastic Engineering",
                "Manufacturing Engineering & Technology", "Automobile Engineering",
                "Mining Engineering", "Mineral Engineering", "Aeronautical Engineering",
                "Computer Engineering", "Computer Science & Technology",
                "Computer Science and Information Technology",
                "Computer Science Engineering (Artificial Intelligence and Machine Learning)",
                "Computer Science & Engineering (Data Science)",
                "Computer Science & Engineering (IoT and Cyber Security Including block chain technology)",
                "Electrical and Computer Engineering", "Electronics and Computer Engineering",
                "Agriculture Engineering", "Applied Electronics & Instrumentation",
                "Integrated M.Sc. in Material Science and Engg",
                "Integrated MSc in Applied Chemistry", "Integrated MSc in Applied Physics",
                "Integrated MSc in Mathematics and Computing", "B ARCH", "B. PLAN"
            ],
            "Diploma": ["Mechanical Engineering", "Computer Science", "Civil Engineering", 
                        "Electronics and Telecommunication"],
            "Degree": ["Science", "Commerce", "Arts", 
                       "B. Tech in Civil Engineering & M.Tech in Structural Engineering",
                       "B. Tech in Electrical Engineering & M.Tech in Power System Engineering"]
        }

        # Group by college name to handle duplicates
        grouped = df.groupby('name')
        for college_name, group in grouped:
            # Use the last row for college data (consistent with previous behavior)
            row = group.iloc[-1]
            college_data = {
                'name': str(row['name']).strip(),
                'state': str(row['state']).strip(),
                'location': str(row['location']).strip().title(),
                'course_level': str(row['course_level']).strip(),
                'fees': float(row['fees']),
                'cutoff_min': float(row['cutoff_min']),
                'cutoff_max': float(row['cutoff_max'])
            }

            # Map course_level
            if college_data['course_level'] == 'UG':
                college_data['course_level'] = 'BTech'
            elif college_data['course_level'] == 'PG':
                college_data['course_level'] = 'Degree'
            elif college_data['course_level'] not in allowed_course_levels:
                logger.warning(f"Invalid course_level '{college_data['course_level']}' for college '{college_data['name']}'")
                continue

            # Validate college data
            if college_data['fees'] < 0 or college_data['cutoff_min'] < 0 or college_data['cutoff_max'] < 0:
                logger.warning(f"Negative values detected for college '{college_data['name']}'")
                continue
            if college_data['cutoff_min'] > college_data['cutoff_max']:
                logger.warning(f"Invalid cutoff range for college '{college_data['name']}'")
                continue

            colleges_data.append(college_data)

            # Process branches for this college (across all rows in the group)
            branches = []
            for _, group_row in group.iterrows():
                for col in branch_columns:
                    if pd.notna(group_row.get(col)):
                        branch_value = str(group_row[col]).strip()
                        if ',' in branch_value or ';' in branch_value:
                            delimiter = ',' if ',' in branch_value else ';'
                            branch_list = [b.strip() for b in branch_value.split(delimiter)]
                            branches.extend(branch_list)
                        else:
                            branches.append(branch_value)

            # Normalize branch names
            branch_mappings = {
                "Computer Science and Engineering": "Computer Science",
                "Electronics & Telecommunication Engineering": "Electronics and Telecommunication",
                "Electronics & Communication Engineering": "Electronics and Telecommunication",
                "Computer Science Engineering (Artificial Intelligence and Machine Learning)": 
                    "Computer Science Engineering (Artificial Intelligence and Machine Learning)",
                "Computer Science & Engineering (Data Science)": "Computer Science & Engineering (Data Science)",
                "Computer Science & Engineering (IoT and Cyber Security Including block chain technology)": 
                    "Computer Science & Engineering (IoT and Cyber Security Including block chain technology)"
            }
            normalized_branches = [branch_mappings.get(b, b) for b in branches]

            # Validate and filter branches
            valid_branches = []
            for branch in normalized_branches:
                if branch and branch in allowed_branches.get(college_data['course_level'], []):
                    valid_branches.append(branch)
                else:
                    logger.warning(f"Invalid or unsupported branch '{branch}' for college '{college_data['name']}'")
            if not valid_branches:
                logger.warning(f"No valid branches for college '{college_data['name']}'")
                continue

            # Add branches to branches_data
            for branch in sorted(set(valid_branches)):
                branches_data.append({
                    'college_name': college_data['name'],
                    'branch': branch
                })

            # Process review data if present
            if has_reviews:
                for _, group_row in group.iterrows():
                    if pd.notna(group_row['college_name']) and pd.notna(group_row['review_text']) and pd.notna(group_row['rating']):
                        review_data = {
                            'college_name': str(group_row['college_name']).strip(),
                            'review_text': str(group_row['review_text']).strip(),
                            'rating': float(group_row['rating'])
                        }
                        if 1 <= review_data['rating'] <= 5:
                            reviews_data.append(review_data)
                        else:
                            logger.warning(f"Invalid rating '{review_data['rating']}' for review of '{review_data['college_name']}'")

        # Update database
        inserted_colleges = 0
        updated_colleges = 0
        inserted_branches = 0
        inserted_reviews = 0

        # Insert or update colleges
        for college_data in colleges_data:
            existing_college = db.query(College).filter(College.name == college_data['name']).first()
            if existing_college:
                # Update existing college
                for key, value in college_data.items():
                    setattr(existing_college, key, value)
                # Delete existing branches to avoid duplicates
                db.query(CollegeBranch).filter(CollegeBranch.college_name == college_data['name']).delete()
                updated_colleges += 1
            else:
                # Insert new college
                db.add(College(**college_data))
                inserted_colleges += 1

        # Insert branches
        for branch_data in branches_data:
            db.add(CollegeBranch(**branch_data))
            inserted_branches += 1

        # Insert reviews
        for review_data in reviews_data:
            if db.query(College).filter(College.name == review_data['college_name']).first():
                db.add(Review(**review_data))
                inserted_reviews += 1
            else:
                logger.warning(f"Cannot add review for non-existent college '{review_data['college_name']}'")

        db.commit()
        logger.info(f"✅ Database updated: {inserted_colleges} colleges inserted, {updated_colleges} colleges updated, {inserted_branches} branches inserted, {inserted_reviews} reviews inserted.")

        # Convert to JSON for response
        # Include branches in the colleges data for the response
        colleges_with_branches = []
        for college in colleges_data:
            college_branches = [b['branch'] for b in branches_data if b['college_name'] == college['name']]
            college_copy = college.copy()
            college_copy['branches'] = college_branches
            colleges_with_branches.append(college_copy)

        json_data = {
            "colleges": colleges_with_branches,
            "reviews": reviews_data,
            "summary": {
                "inserted_colleges": inserted_colleges,
                "updated_colleges": updated_colleges,
                "inserted_branches": inserted_branches,
                "inserted_reviews": inserted_reviews
            }
        }
        return json_data

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error processing Excel file: {e}")
        raise
    finally:
        db.close()
