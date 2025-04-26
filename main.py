from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine, Base
from models import College, Review
from sqlalchemy.sql import text
from typing import List, Dict, Optional
import os


from fastapi.staticfiles import StaticFiles



# Initialize FastAPI

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")

# Your existing route handlers...




# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Only run this if executed directly (not when imported)


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

# State and location mappings for suggestions
STATE_MAPPINGS = {
    "utt": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "mh": "Maharashtra",
    "kar": "Karnataka",
    "tn": "Tamil Nadu"
}

LOCATION_MAPPINGS = {
    "mu": "Mumbai",
    "che": "Chennai",
    "ban": "Bangalore",
    "hyd": "Hyderabad",
    "del": "Delhi"
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_college_data() -> List[Dict]:
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        reviews = db.query(Review).all()

        colleges_dict = {}
        for college in colleges:
            key = (college.name, college.state, college.location, college.course_level)
            if key not in colleges_dict:
                colleges_dict[key] = {
                    "id": college.id,
                    "name": college.name,
                    "state": college.state,
                    "location": college.location,
                    "course_level": "Undergraduate" if college.course_level == "UG" else "Postgraduate",
                    "min_score": float(college.cutoff),
                    "fees": float(college.fees),
                    "reviews": [],
                    "avg_rating": 0.0
                }

        colleges_list = list(colleges_dict.values())

        # Calculate average ratings
        for review in reviews:
            for college in colleges_list:
                if college["name"] == review.college_name:
                    college["reviews"].append({
                        "review_text": review.review_text,
                        "rating": float(review.rating)
                    })
        
        for college in colleges_list:
            if college["reviews"]:
                college["avg_rating"] = sum(r["rating"] for r in college["reviews"]) / len(college["reviews"])

        return colleges_list
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        db.close()

def get_suggestions(colleges: List[Dict], query: str, field: str) -> List[str]:
    suggestions = set()
    query = query.lower()
    for college in colleges:
        value = college[field].lower()
        if query in value:
            suggestions.add(college[field])
    return sorted(suggestions)

# Your existing route handlers...
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Your existing index implementation


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
        {
            "request": request,
            "results": [],
            "suggestions": suggestions,
            "error": None,
            "form_data": {}
        }  pass
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
    error = None
    results = []
    form_data = {
        "course_level": course_level,
        "state": state,
        "location": location,
        "college_name": college_name,
        "fees": fees,
        "score": score
    }

    # Validate mandatory fields
    if not course_level or not state:
        error = "Course level and state are required fields."
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {
                    "college_name": get_suggestions(colleges, college_name, "name"),
                    "location": get_suggestions(colleges, location, "location"),
                    "state": get_suggestions(colleges, state, "state")
                },
                "error": error,
                "form_data": form_data
            } pass
        )

    # Apply state mapping
    state_lower = state.lower()
    if state_lower in STATE_MAPPINGS:
        state = STATE_MAPPINGS[state_lower]

    # Apply location mapping
    location_lower = location.lower()
    if location_lower in LOCATION_MAPPINGS:
        location = LOCATION_MAPPINGS[location_lower]

    # Filter colleges
    filtered = [
        c for c in colleges
        if c["course_level"].lower() == course_level.lower()
        and c["state"].lower() == state.lower()
    ]

    # Apply location filter if provided
    if location:
        filtered = [c for c in filtered if location.lower() in c["location"].lower()]

    # Apply college name filter if provided
    if college_name:
        filtered = [c for c in filtered if college_name.lower() in c["name"].lower()]

    # Apply fees range filter if provided
    if fees:
        try:
            fees_value = float(fees)
            # Define fee ranges (e.g., 180000 → 100000-200000)
            lower_fee = (fees_value // 100000) * 100000
            upper_fee = lower_fee + 100000
            filtered = [c for c in filtered if lower_fee <= c["fees"] <= upper_fee]
        except ValueError:
            pass  # Ignore invalid fee inputs

    # Apply score range filter if provided
    if score:
        try:
            score_value = float(score)
            # Define score ranges (e.g., 1001 → 1000-10000)
            if score_value < 1000:
                lower_score = 0
                upper_score = 1000
            else:
                lower_score = (score_value // 1000) * 1000
                upper_score = lower_score + 9000  # Creates a 1000-10000 range
            filtered = [c for c in filtered if lower_score <= c["min_score"] <= upper_score]
        except ValueError:
            pass  # Ignore invalid score inputs

    # Deduplicate results
    seen = set()
    results = [
        x for x in filtered
        if not ((x["name"], x["state"], x["location"]) in seen
        or seen.add((x["name"], x["state"], x["location"]))
    ]

    # Sort results by rating (higher first) then by fees (lower first)
    results.sort(key=lambda x: (-x["avg_rating"], x["fees"]))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": results,
            "suggestions": {
                "college_name": get_suggestions(colleges, college_name, "name"),
                "location": get_suggestions(colleges, location, "location"),
                "state": get_suggestions(colleges, state, "state")
            },
            "error": None,
            "form_data": form_data
        }
    )


