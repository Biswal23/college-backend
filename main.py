from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, engine
from models import Base, College, CollegeBranch, Review
import initial_data
import pandas as pd
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
class CollegeResponse(BaseModel):
    name: str
    state: str
    location: str
    course_level: str
    fees: float
    min_score: float
    max_score: float
    rank: Optional[int]
    branches: List[str]
    avg_rating: Optional[float]
    reviews: List[dict]

class SearchRequest(BaseModel):
    course_level: Optional[str]
    state: Optional[str]
    location: Optional[str]
    college_name: Optional[str]
    branch: Optional[str]
    fees: Optional[float]
    score: Optional[float]

# Function to process Excel file (for developers)
def process_excel_file(content: bytes):
    try:
        db = SessionLocal()
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "form_data": {}, "results": [], "error": None, "success_message": None, "use_table": False})

@app.post("/api/search", response_model=List[CollegeResponse])
async def search_colleges(search: SearchRequest):
    db = SessionLocal()
    try:
        query = db.query(College)
        if search.course_level:
            query = query.filter(College.course_level == search.course_level)
        if search.state:
            query = query.filter(College.state.ilike(f"%{search.state}%"))
        if search.location:
            query = query.filter(College.location.ilike(f"%{search.location}%"))
        if search.college_name:
            query = query.filter(College.name.ilike(f"%{search.college_name}%"))
        if search.fees is not None:
            query = query.filter(College.fees <= search.fees)
        if search.score is not None:
            query = query.filter(College.min_score <= search.score, College.max_score >= search.score)
        if search.branch:
            query = query.join(CollegeBranch).filter(CollegeBranch.branch.ilike(f"%{search.branch}%"))

        colleges = query.all()
        result = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            reviews = [{"review_text": r.review_text, "rating": r.rating} for r in college.reviews]
            avg_rating = sum(r.rating for r in college.reviews) / len(college.reviews) if college.reviews else 0
            result.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "fees": college.fees,
                "min_score": college.min_score,
                "max_score": college.max_score,
                "rank": college.rank,
                "branches": branches,
                "avg_rating": avg_rating,
                "reviews": reviews
            })
        return result
    finally:
        db.close()

@app.get("/api/suggestions")
async def get_suggestions():
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        branches = db.query(CollegeBranch).all()
        return {
            "college_name": list(set(c.name for c in colleges)),
            "state": list(set(c.state for c in colleges)),
            "location": list(set(c.location for c in colleges)),
            "branch": list(set(b.branch for b in branches))
        }
    finally:
        db.close()

@app.get("/api/results", response_model=List[CollegeResponse])
async def get_results(score: Optional[float] = None):
    db = SessionLocal()
    try:
        query = db.query(College)
        if score is not None:
            query = query.filter(College.min_score <= score, College.max_score >= score)
        colleges = query.all()
        result = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            reviews = [{"review_text": r.review_text, "rating": r.rating} for r in college.reviews]
            avg_rating = sum(r.rating for r in college.reviews) / len(college.reviews) if college.reviews else 0
            result.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "fees": college.fees,
                "min_score": college.min_score,
                "max_score": college.max_score,
                "rank": college.rank,
                "branches": branches,
                "avg_rating": avg_rating,
                "reviews": reviews
            })
        return result
    finally:
        db.close()

@app.get("/api/rank", response_model=List[CollegeResponse])
async def get_rank(rank: Optional[int] = None):
    db = SessionLocal()
    try:
        query = db.query(College)
        if rank is not None:
            # Fetch colleges within ±10 ranks for flexibility
            query = query.filter(College.rank.between(rank - 10, rank + 10))
        colleges = query.all()
        result = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            reviews = [{"review_text": r.review_text, "rating": r.rating} for r in college.reviews]
            avg_rating = sum(r.rating for r in college.reviews) / len(college.reviews) if college.reviews else 0
            result.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "fees": college.fees,
                "min_score": college.min_score,
                "max_score": college.max_score,
                "rank": college.rank,
                "branches": branches,
                "avg_rating": avg_rating,
                "reviews": reviews
            })
        return result
    finally:
        db.close()
