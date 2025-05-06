from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, Base
from models import College, Review
from typing import Optional
from sqlalchemy.orm import Session
import os
from initial_data import initialize_database

# Initialize FastAPI app
app = FastAPI()

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")



# Create database tables and initialize data
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    # Verify schema
    db = SessionLocal()
    try:
        db.execute("SELECT cutoff_min, cutoff_max FROM colleges LIMIT 1")
        print("✅ Schema verified: 'cutoff_min' and 'cutoff_max' columns exist")
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
    finally:
        db.close()
except Exception as e:
    print(f"❌ Error creating database tables: {e}")

# Initialize database with sample data
try:
    initialize_database(first_init=True)  # Use first_init=True only for first deployment
    db = SessionLocal()
    college_count = db.query(College).count()
    if college_count == 0:
        print("❌ Warning: Database is empty after initialization!")
    else:
        print(f"✅ Database initialized with {college_count} colleges")
    db.close()
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    
# College name mappings to normalize user input
COLLEGE_MAPPINGS = {
    "tech college": "Tech College",
    "science college": "Science College",
    "eng college": "Engineering College",
    "commerce institute": "Commerce Institute",
    "polytechnic institute": "Polytechnic Institute",
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/", response_class=HTMLResponse)
async def index_post(
    request: Request,
    course_level: str = Form(...),
    state: Optional[str] = Form(default=""),
    location: Optional[str] = Form(default=""),
    college_name: Optional[str] = Form(default=""),
    branch: Optional[str] = Form(default=""),
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default="")
):
    db = SessionLocal()
    try:
        # Validation
        if not course_level:
            raise HTTPException(status_code=400, detail="Course level is required.")
        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if course_level not in allowed_course_levels:
            raise HTTPException(status_code=400, detail=f"Course level must be one of {allowed_course_levels}.")

        # Normalize inputs
        state = state.strip().title() if state else ""
        location = location.strip().title() if location else ""
        college_name = college_name.strip().title() if college_name else ""
        branch = branch.strip().title() if branch else ""

        # Apply college name mapping
        college_name_lower = college_name.lower()
        if college_name_lower in COLLEGE_MAPPINGS:
            college_name = COLLEGE_MAPPINGS[college_name_lower]
        print(f"POST /: Inputs - course_level: {course_level}, state: {state}, location: {location}, college_name: {college_name}, branch: {branch}, fees: {fees}, score: {score}")

        # Check if database is empty
        all_colleges = db.query(College).all()
        if not all_colleges:
            print("POST /: Error: Database is empty!")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "results": [],
                    "suggestions": {"college_name": [], "location": [], "state": [], "branch": []},
                    "error": "No colleges available in the database. Please try again later or contact support.",
                    "form_data": {
                        "course_level": course_level,
                        "state": state,
                        "location": location,
                        "college_name": college_name,
                        "branch": branch,
                        "fees": fees,
                        "score": score
                    },
                    "seo": {
                        "title": "College Search - No Data",
                        "description": "No colleges available in the database.",
                        "keywords": "college search, India",
                        "og_title": "College Search - No Data",
                        "og_description": "No colleges available in the database.",
                        "og_url": str(request.url),
                        "twitter_card": "summary"
                    },
                    "use_table": False
                }
            )

        # Base query
        query = db.query(College).filter(College.course_level == course_level)

        # Apply filters with case-insensitive partial matching
        if state:
            query = query.filter(College.state.ilike(f"%{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"%{location}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"%{college_name}%"))
        if branch:
            query = query.filter(College.branch.ilike(f"%{branch}%"))
        if fees:
            try:
                fees_value = float(fees)
                lower_fee = (fees_value // 100000) * 100000
                upper_fee = lower_fee + 100000
                query = query.filter(College.fees.between(lower_fee, upper_fee))
            except ValueError:
                print(f"POST /: Invalid fees input: {fees}")
        if score:
            try:
                score_value = float(score)
                query = query.filter(College.cutoff_min <= score_value, College.cutoff_max >= score_value)
            except ValueError:
                print(f"POST /: Invalid score input: {score}")

        colleges = query.all()
        print(f"POST /: Query results count: {len(colleges)}")

        # If no optional filters, show all for the mandatory course_level
        if not any([state, location, college_name, branch, fees, score]):
            colleges = db.query(College).filter(College.course_level == course_level).all()
            print(f"POST /: All colleges for {course_level}: {len(colleges)}")

        # Format results
        results = []
        for college in colleges:
            reviews = db.query(Review).filter(Review.college_name == college.name).all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
            results.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "branch": college.branch,
                "min_score": college.cutoff_min,
                "max_score": college.cutoff_max,
                "fees": college.fees,
                "avg_rating": avg_rating,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews[:2]]
            })

        # Generate autosuggestions based on all colleges
        suggestions = {
            "college_name": sorted(
                [c.name for c in all_colleges if c.name],
                key=lambda x: x.lower()
            ),
            "location": sorted(
                [c.location for c in all_colleges if c.location],
                key=lambda x: x.lower()
            ),
            "state": sorted(
                [c.state for c in all_colleges if c.state],
                key=lambda x: x.lower()
            ),
            "branch": sorted(
                [c.branch for c in all_colleges if c.branch],
                key=lambda x: x.lower()
            )
        }
        print(f"POST /: Generated suggestions: {suggestions}")

        # Check for invalid inputs and provide specific error messages
        error_message = None
        if not results:
            existing_college_names = [c.name for c in all_colleges]
            existing_locations = [c.location for c in all_colleges if c.location]
            existing_states = [c.state for c in all_colleges if c.state]
            existing_branches = [c.branch for c in all_colleges if c.branch]

            if state and not any(state.lower() in s.lower() for s in existing_states):
                error_message = f"No colleges found for state '{state}'. Try a different state."
            elif location and not any(location.lower() in loc.lower() for loc in existing_locations):
                error_message = f"No colleges found for location '{location}'. Try a different location."
            elif college_name and not any(college_name.lower() in name.lower() for name in existing_college_names):
                error_message = f"No colleges found for college name '{college_name}'. Try a different name."
            elif branch and not any(branch.lower() in b.lower() for b in existing_branches):
                error_message = f"No colleges found for branch '{branch}'. Try a different branch."
            elif score and not score.replace(".", "").isdigit():
                error_message = f"Invalid score '{score}'. Please enter a valid number."
            else:
                error_message = f"No colleges found for {course_level} with the given criteria. Try broadening your search."

        # SEO metadata for search results
        states = sorted(set(c.state for c in colleges if c.state))
        locations = sorted(set(c.location for c in colleges if c.location))
        seo_metadata = {
            "title": f"Top {course_level} Colleges in {state or 'India'} | Search Results",
            "description": f"Find {course_level} colleges in {state or 'India'}, {location or 'various districts'}. Filter by fees, cutoff score, and branch.",
            "keywords": f"{course_level} colleges, {state or 'India'}, {location or 'districts'}, {', '.join(suggestions['branch'][:3])}, college search",
            "og_title": f"Search {course_level} Colleges in {state or 'India'}",
            "og_description": f"Explore {course_level} colleges in {state or 'India'} with filters for cutoff, fees, and more.",
            "og_url": str(request.url),
            "twitter_card": "summary_large_image"
        }

        context = {
            "request": request,
            "results": sorted(results, key=lambda x: (-x["avg_rating"], x["fees"])),
            "suggestions": suggestions,
            "error": error_message,
            "form_data": {
                "course_level": course_level,
                "state": state,
                "location": location,
                "college_name": college_name,
                "branch": branch,
                "fees": fees,
                "score": score
            },
            "seo": seo_metadata,
            "use_table": len(results) > 5
        }
        print(f"POST /: Context passed to template: {context}")
        return templates.TemplateResponse("index.html", context)

    except Exception as e:
        print(f"❌ POST /: Search error: {e}")
        seo_metadata = {
            "title": "Error - College Search",
            "description": "An error occurred while searching for colleges.",
            "keywords": "college search, India",
            "og_title": "Error - College Search",
            "og_description": "An error occurred while searching for colleges.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {"college_name": [], "location": [], "state": [], "branch": []},
                "error": "An error occurred while searching. Please try again or contact support.",
                "form_data": {
                    "course_level": course_level,
                    "state": state,
                    "location": location,
                    "college_name": college_name,
                    "branch": branch,
                    "fees": fees,
                    "score": score
                },
                "seo": seo_metadata,
                "use_table": False
            }
        )
    finally:
        db.close()
