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

# Initialize FastAPI app
app = FastAPI()

# Initialize database
initialize_database()

# Mount static files if directory exists
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
            "college_name": sorted(set(c.name for c in colleges), key=str.lower),
            "location": sorted(set(c.location for c in colleges if c.location), key=str.lower),
            "state": sorted(set(c.state for c in colleges if c.state), key=str.lower)
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
    state: Optional[str] = Form(default=""),
    location: Optional[str] = Form(default=""),
    college_name: Optional[str] = Form(default=""),
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default="")
):
    db = SessionLocal()
    try:
        # Validation
        if not course_level:
            raise HTTPException(status_code=400, detail="Course level is required.")

        # Apply mappings
        state_lower = state.lower() if state else ""
        if state_lower in STATE_MAPPINGS:
            state = STATE_MAPPINGS[state_lower]

        location_lower = location.lower() if location else ""
        if location_lower in LOCATION_MAPPINGS:
            location = LOCATION_MAPPINGS[location_lower]

        # Base query
        query = db.query(College).filter(
            College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
        )

        # Filters with case-insensitive prefix matching
        if state:
            query = query.filter(College.state.ilike(f"{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"{location}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"{college_name}%"))
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

        # If no optional filters are provided, show all colleges for the mandatory course_level
        if not any([state, location, college_name, fees, score]):
            colleges = db.query(College).filter(
                College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
            ).all()

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

        # Suggestions with prefix matching
        all_colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted(
                [c.name for c in all_colleges if not college_name or c.name.lower().startswith(college_name.lower())],
                key=str.lower
            ),
            "location": sorted(
                [c.location for c in all_colleges if c.location and (not location or c.location.lower().startswith(location.lower()))],
                key=str.lower
            ),
            "state": sorted(
                [c.state for c in all_colleges if c.state and (not state or c.state.lower().startswith(state.lower()))],
                key=str.lower
            )
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

# Manual entry for adding a new college
@app.post("/add_college", response_class=HTMLResponse)
async def add_college(
    request: Request,
    name: str = Form(...),
    state: str = Form(...),
    location: str = Form(...),
    course_level: str = Form(...),
    fees: float = Form(...),
    cutoff: float = Form(...),
    review_text: Optional[str] = Form(default=""),
    rating: Optional[int] = Form(default=None)
):
    db = SessionLocal()
    try:
        # Validate inputs
        if not all([name, state, location, course_level, fees, cutoff]):
            raise HTTPException(status_code=400, detail="All fields except review and rating are required.")
        
        if course_level.lower() not in ["undergraduate", "postgraduate"]:
            raise HTTPException(status_code=400, detail="Course level must be Undergraduate or Postgraduate.")
        
        if fees < 0:
            raise HTTPException(status_code=400, detail="Fees cannot be negative.")
        
        if cutoff < 0:
            raise HTTPException(status_code=400, detail="Cutoff score cannot be negative.")
        
        if rating and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

        # Check if college already exists
        existing_college = db.query(College).filter(College.name == name).first()
        if existing_college:
            raise HTTPException(status_code=400, detail="College with this name already exists.")

        # Create new college
        new_college = College(
            name=name,
            state=state,
            location=location,
            course_level="UG" if course_level.lower() == "undergraduate" else "PG",
            fees=fees,
            cutoff=cutoff
        )
        db.add(new_college)
        db.commit()
        db.refresh(new_college)

        # Add review if provided
        if review_text and rating:
            new_review = Review(
                college_name=name,
                review_text=review_text,
                rating=rating
            )
            db.add(new_review)
            db.commit()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {
                    "college_name": sorted(set(c.name for c in db.query(College).all()), key=str.lower),
                    "location": sorted(set(c.location for c in db.query(College).all() if c.location), key=str.lower),
                    "state": sorted(set(c.state for c in db.query(College).all() if c.state), key=str.lower)
                },
                "error": None,
                "form_data": {},
                "success_message": f"College {name} added successfully!"
            }
        )

    except Exception as e:
        print(f"❌ Error adding college: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {"college_name": [], "location": [], "state": []},
                "error": f"Error adding college: {str(e)}",
                "form_data": {}
            }
        )
    finally:
        db.close()

# Health check route
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API route to list all colleges
@app.get("/api/colleges")
def list_colleges():
    db = SessionLocal()
    colleges = db.query(College).all()
    db.close()
    return colleges
