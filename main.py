from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from database import SessionLocal, engine, Base
from models import College, Review
from sqlalchemy.sql import text
from typing import List, Dict
import os

app = FastAPI()

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

def load_college_data() -> List[Dict]:
    db = SessionLocal()
    try:
        # Load colleges using SQLAlchemy
        colleges = db.query(College).all()
        reviews = db.query(Review).all()

        # Map colleges to dictionary format
        colleges_dict = {}
        for college in colleges:
            key = (college.name, college.state, college.location, college.course_level)
            if key not in colleges_dict:
                colleges_dict[key] = {
                    "name": college.name,
                    "state": college.state,
                    "location": college.location,
                    "course_level": "Undergraduate" if college.course_level == "UG" else "Postgraduate",
                    "min_score": float(college.cutoff),
                    "fees": float(college.fees),
                    "reviews": []
                }

        colleges_list = list(colleges_dict.values())

        # Attach reviews to corresponding colleges
        for review in reviews:
            for college in colleges_list:
                if college["name"] == review.college_name:
                    college["reviews"].append({
                        "review_text": review.review_text,
                        "rating": float(review.rating)
                    })

        return colleges_list
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    colleges = load_college_data()
    locations = sorted(set(c["location"] for c in colleges if c["location"]))
    college_names = sorted(set(c["name"] for c in colleges if c["name"]))
    states = sorted(set(c["state"] for c in colleges if c["state"]))
    suggestions = {
        "college_name": college_names,
        "location": locations,
        "state": states
    }
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "results": [], "suggestions": suggestions, "error": None}
    )

@app.post("/", response_class=HTMLResponse)
async def index_post(
    request: Request,
    course_level: str = Form(...),
    state: str = Form(default=""),
    location: str = Form(default=""),
    college_name: str = Form(default=""),
    fees: str = Form(default=""),
    score: str = Form(default="")
):
    colleges = load_college_data()
    locations = sorted(set(c["location"] for c in colleges if c["location"]))
    college_names = sorted(set(c["name"] for c in colleges if c["name"]))
    states = sorted(set(c["state"] for c in colleges if c["state"]))
    suggestions = {
        "college_name": college_names,
        "location": locations,
        "state": states
    }
    error = None
    results = []

    if not course_level or not state:
        error = "Course level and state are required."
    else:
        filtered = colleges
        filtered = [
            c for c in filtered
            if c["course_level"].lower() == course_level.lower()
            and c["state"].lower() == state.lower()
        ]
        if location:
            filtered = [c for c in filtered if location.lower() in c["location"].lower()]
        if college_name:
            filtered = [c for c in filtered if college_name.lower() in c["name"].lower()]
        if fees:
            try:
                max_fees = float(fees)
                filtered = [c for c in filtered if c["fees"] <= max_fees]
            except ValueError:
                pass
        if score:
            try:
                min_score = float(score)
                filtered = [c for c in filtered if c["min_score"] <= min_score]
            except ValueError:
                pass
        # Deduplicate results
        seen = set()
        results = [
            x for x in filtered
            if not ((x["name"], x["state"], x["location"], x["course_level"]) in seen
                    or seen.add((x["name"], x["state"], x["location"], x["course_level"])))
        ]

        if college_name:
            suggestions["college_name"] = [n for n in college_names if college_name.lower() in n.lower()]
        if location:
            suggestions["location"] = [l for l in locations if location.lower() in l.lower()]
        if state:
            suggestions["state"] = [s for s in states if state.lower() in s.lower()]

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "results": results, "suggestions": suggestions, "error": error}
    )

@app.post("/api/search")
async def search(
    course_level: str = Form(...),
    state: str = Form(default=""),
    location: str = Form(default=""),
    college_name: str = Form(default=""),
    fees: str = Form(default=""),
    score: str = Form(default="")
):
    colleges = load_college_data()
    if not course_level or not state:
        raise HTTPException(status_code=400, detail="Course level and state are required")

    filtered = colleges
    filtered = [
        c for c in filtered
        if c["course_level"].lower() == course_level.lower()
        and c["state"].lower() == state.lower()
    ]
    if location:
        filtered = [c for c in filtered if location.lower() in c["location"].lower()]
    if college_name:
        filtered = [c for c in filtered if college_name.lower() in c["name"].lower()]
    if fees:
        try:
            max_fees = float(fees)
            filtered = [c for c in filtered if c["fees"] <= max_fees]
        except ValueError:
            pass
    if score:
        try:
            min_score = float(score)
            filtered = [c for c in filtered if c["min_score"] <= min_score]
        except ValueError:
            pass
    # Deduplicate results
    seen = set()
    results = [
        x for x in filtered
        if not ((x["name"], x["state"], x["location"], x["course_level"]) in seen
                or seen.add((x["name"], x["state"], x["location"], x["course_level"])))
    ]
    suggestions = {
        "college_name": sorted(
            set(c["name"] for c in colleges if c["name"] and
                (not college_name or college_name.lower() in c["name"].lower())),
            key=lambda x: x.lower()
        ),
        "location": sorted(
            set(c["location"] for c in colleges if c["location"] and
                (not location or location.lower() in c["location"].lower())),
            key=lambda x: x.lower()
        ),
        "state": sorted(
            set(c["state"] for c in colleges if c["state"] and
                (not state or state.lower() in c["state"].lower())),
            key=lambda x: x.lower()
        )
    }
    return {"results": results, "suggestions": suggestions}

@app.post("/api/submit_review")
async def submit_review(
    college_name: str = Form(...),
    review_text: str = Form(...),
    rating: str = Form(...)
):
    if not (college_name and review_text and rating):
        raise HTTPException(status_code=400, detail="College name, review text, and rating are required")

    try:
        rating = float(rating)
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rating format")

    db = SessionLocal()
    try:
        # Check if college exists
        college = db.query(College).filter(College.name == college_name).first()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")

        # Add review
        new_review = Review(
            college_name=college_name,
            review_text=review_text,
            rating=rating
        )
        db.add(new_review)
        db.commit()
        return {"message": "Review submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@app.get("/api/version")
async def get_sqlite_version():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT sqlite_version()"))
        version = result.fetchone()[0]
        return {"message": f"SQLite version: {version}"}
    finally:
        db.close()
