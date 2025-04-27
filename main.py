from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, Base
from models import College, Review
from typing import List, Dict, Optional
import os

# At the top with other imports
from initial_data import initialize_database

# Right after creating FastAPI app
initialize_database()  # This will create tables and add sample data if empty
# Initialize FastAPI
app = FastAPI()

# Only mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")

# Mappings
STATE_MAPPINGS = {
    "utt": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "mah": "Maharashtra",
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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted(set(c.name for c in colleges)),
            "location": sorted(set(c.location for c in colleges if c.location)),
            "state": sorted(set(c.state for c in colleges if c.state))
        }
    except Exception as e:
        print(f"❌ Error loading suggestions: {e}")
        suggestions = {"college_name": [], "location": [], "state": []}
    finally:
        db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": [],
            "suggestions": suggestions,
            "error": None,
            "form_data": {}
        }
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
    db = SessionLocal()
    try:
        # Validation
        if not course_level or not state:
            raise HTTPException(status_code=400, detail="Course level and state are required.")

        # Apply mappings
        state_lower = state.lower()
        if state_lower in STATE_MAPPINGS:
            state = STATE_MAPPINGS[state_lower]

        location_lower = location.lower()
        if location_lower in LOCATION_MAPPINGS:
            location = LOCATION_MAPPINGS[location_lower]

        # Base query
        query = db.query(College).filter(
            College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
        )

        # Filters
        if state:
            query = query.filter(College.state.ilike(f"%{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"%{location}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"%{college_name}%"))
        if fees:
            try:
                fees_value = float(fees)
                lower_fee = (fees_value // 100000) * 100000
                upper_fee = lower_fee + 100000
                query = query.filter(College.fees.between(lower_fee, upper_fee))
            except ValueError:
                pass
        if score:
            try:
                score_value = float(score)
                if score_value < 1000:
                    lower_score = 0
                    upper_score = 1000
                else:
                    lower_score = (score_value // 1000) * 1000
                    upper_score = lower_score + 9000
                query = query.filter(College.cutoff.between(lower_score, upper_score))
            except ValueError:
                pass

        colleges = query.all()

        # Format results
        results = []
        for college in colleges:
            reviews = db.query(Review).filter(Review.college_name == college.name).all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

            results.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": "Undergraduate" if college.course_level == "UG" else "Postgraduate",
                "min_score": college.cutoff,
                "fees": college.fees,
                "avg_rating": avg_rating,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews[:2]]
            })

        # Suggestions for the form dropdowns
        all_colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted(set(c.name for c in all_colleges)),
            "location": sorted(set(c.location for c in all_colleges if c.location)),
            "state": sorted(set(c.state for c in all_colleges if c.state))
        }

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": sorted(results, key=lambda x: (-x["avg_rating"], x["fees"])),
                "suggestions": suggestions,
                "error": None if results else "No colleges found matching your criteria.",
                "form_data": {
                    "course_level": course_level,
                    "state": state,
                    "location": location,
                    "college_name": college_name,
                    "fees": fees,
                    "score": score
                }
            }
        )

    except Exception as e:
        print(f"❌ Search error: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {"college_name": [], "location": [], "state": []},
                "error": "An error occurred while searching. Please try again.",
                "form_data": {
                    "course_level": course_level,
                    "state": state,
                    "location": location,
                    "college_name": college_name,
                    "fees": fees,
                    "score": score
                }
            }
        )
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
