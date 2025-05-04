from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, engine
from models import Base, College, CollegeBranch, Review
import initial_data
import pandas as pd
import logging
import requests
import io
import os

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

# Function to fetch and process CSV file from GitHub
def process_csv_file(github_url: str = os.getenv("GITHUB_CSV_URL", "https://raw.githubusercontent.com/username/repo/main/college_data.csv")):
    try:
        db = SessionLocal()
        # Fetch CSV from GitHub
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        # Read CSV content into a pandas DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        
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
        logger.info(f"Successfully processed CSV file: {summary}")
        return {'status': 'success', 'summary': summary}
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# Endpoint to trigger CSV processing (for developers or on startup)
@app.on_event("startup")
async def startup_event():
    try:
        result = process_csv_file()
        logger.info(f"Startup CSV processing result: {result}")
    except Exception as e:
        logger.error(f"Error during startup CSV processing: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    seo = {
        "title": "College Finder - Search for Top Colleges",
        "description": "Find the best colleges based on course level, state, location, fees, and more.",
        "keywords": "college finder, college search, education, higher education, BTech, Diploma, Degree",
        "og_title": "College Finder",
        "og_description": "Search for colleges that match your preferences and academic profile.",
        "og_url": str(request.url),
        "twitter_card": "summary"
    }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "form_data": {},
            "results": [],
            "error": None,
            "success_message": None,
            "use_table": False,
            "seo": seo
        }
    )

@app.post("/", response_class=HTMLResponse)
async def search_form(
    request: Request,
    course_level: str = Form(...),
    state: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    college_name: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    fees: Optional[float] = Form(None),
    score: Optional[float] = Form(None)
):
    search_data = SearchRequest(
        course_level=course_level,
        state=state,
        location=location,
        college_name=college_name,
        branch=branch,
        fees=fees,
        score=score
    )
    db = SessionLocal()
    try:
        query = db.query(College)
        if search_data.course_level:
            query = query.filter(College.course_level == search_data.course_level)
        if search_data.state:
            query = query.filter(College.state.ilike(f"%{search_data.state}%"))
        if search_data.location:
            query = query.filter(College.location.ilike(f"%{search_data.location}%"))
        if search_data.college_name:
            query = query.filter(College.name.ilike(f"%{search_data.college_name}%"))
        if search_data.fees is not None:
            query = query.filter(College.fees <= search_data.fees)
        if search_data.score is not None:
            query = query.filter(College.min_score <= search_data.score, College.max_score >= search_data.score)
        if search_data.branch:
            query = query.join(CollegeBranch).filter(CollegeBranch.branch.ilike(f"%{search_data.branch}%"))

        colleges = query.all()
        results = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            reviews = [{"review_text": r.review_text, "rating": r.rating} for r in college.reviews]
            avg_rating = sum(r.rating for r in college.reviews) / len(college.reviews) if college.reviews else 0
            results.append({
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
        seo = {
            "title": "College Finder - Search Results",
            "description": "View college search results based on your preferences.",
            "keywords": "college search results, college finder, education",
            "og_title": "College Finder - Search Results",
            "og_description": "Find colleges matching your criteria.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "form_data": search_data.dict(),
                "results": results,
                "error": None,
                "success_message": f"Found {len(results)} colleges matching your criteria.",
                "use_table": len(results) > 5,
                "seo": seo
            }
        )
    except Exception as e:
        logger.error(f"Error processing search: {e}")
        seo = {
            "title": "College Finder - Search Error",
            "description": "An error occurred while searching for colleges.",
            "keywords": "college finder, college search, education",
            "og_title": "College Finder - Search Error",
            "og_description": "An error occurred while searching for colleges.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "form_data": search_data.dict(),
                "results": [],
                "error": "An error occurred while searching. Please try again.",
                "success_message": None,
                "use_table": False,
                "seo": seo
            }
        )
    finally:
        db.close()

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
