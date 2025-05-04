import pandas as pd
import io
from sqlalchemy.orm import Session
from models import College, CollegeBranch, Review
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_excel_file(content: bytes, db: Session):
    try:
        df = pd.read_excel(io.BytesIO(content))
        summary = {'inserted_colleges': 0, 'inserted_branches': 0, 'inserted_reviews': 0}

        for _, row in df.iterrows():
            college = db.query(College).filter_by(name=row['name'], state=row['state'], location=row['location']).first()
            if not college:
                college = College(
                    name=row['name'],
                    state=row['state'],
                    location=row['location'],
                    course_level=row['course_level'],
                    fees=row['fees'],
                    min_score=row['min_score'],
                    max_score=row['max_score'],
                    rank=row['rank'] if pd.notna(row['rank']) else None
                )
                db.add(college)
                summary['inserted_colleges'] += 1
            else:
                college.fees = row['fees']
                college.min_score = row['min_score']
                college.max_score = row['max_score']
                college.rank = row['rank'] if pd.notna(row['rank']) else None

            # Handle branches
            branches = row['branches'].split(',') if isinstance(row['branches'], str) else []
            for branch_name in branches:
                branch_name = branch_name.strip()
                branch = db.query(CollegeBranch).filter_by(college_name=college.name, branch=branch_name).first()
                if not branch:
                    branch = CollegeBranch(college_name=college.name, branch=branch_name)
                    db.add(branch)
                    summary['inserted_branches'] += 1

            # Handle reviews
            if 'review_text' in row and 'rating' in row and pd.notna(row['review_text']) and pd.notna(row['rating']):
                review = Review(
                    college_name=college.name,
                    review_text=row['review_text'],
                    rating=row['rating']
                )
                db.add(review)
                summary['inserted_reviews'] += 1

        db.commit()
        return {'status': 'success', 'summary': summary}
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing Excel file: {e}")
        raise
