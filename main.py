from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, Base
from models import College, Review
from typing import Optional
from sqlalchemy.orm import Session
import os
from initial_data import initialize_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()
app.state.suggestions = {"college_name": [], "location": [], "state": [], "branch": []}

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# College name mappings to normalize user input
COLLEGE_MAPPINGS = {
    "tech college": "Tech College",
    "science college": "Science College",
    "eng college": "Engineering College",
    "commerce institute": "Commerce Institute",
    "polytechnic institute": "Polytechnic Institute",
}

# Helper functions for deduplication and formatting
def get_deduplicated_colleges(query, db: Session):
    colleges = query.all()
    seen = set()
    deduplicated = []
    for college in colleges:
        key = (college.name, college.state, college.location, college.course_level, college.branch)
        if key not in seen:
            seen.add(key)
            deduplicated.append(college)
    return deduplicated

def format_college_results(colleges, db: Session):
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
    return sorted(results, key=lambda x: (-x["avg_rating"], x["fees"]))

def clean_duplicates(db: Session):
    try:
        colleges = db.query(College).all()
        seen = set()
        for college in colleges:
            key = (college.name, college.state, college.location, college.course_level, college.branch)
            if key in seen:
                db.delete(college)
            else:
                seen.add(key)
        db.commit()
        logger.info("✅ Removed duplicate colleges")
    except Exception as e:
        logger.error(f"❌ Error cleaning duplicates: {e}")

def normalize_case(db: Session):
    try:
        colleges = db.query(College).all()
        for college in colleges:
            college.name = college.name.title()
            college.state = college.state.title() if college.state else college.state
            college.location = college.location.title() if college.location else college.location
            college.branch = college.branch.title() if college.branch else college.branch
        db.commit()
        logger.info("✅ Normalized case in database")
    except Exception as e:
        logger.error(f"❌ Error normalizing case: {e}")

def update_suggestions(db: Session):
    colleges = db.query(College).all()
    app.state.suggestions = {
        "college_name": sorted([c.name for c in colleges], key=lambda x: x.lower()),
        "location": sorted([c.location for c in colleges if c.location], key=lambda x: x.lower()),
        "state": sorted(list(set(c.state for c in colleges if c.state)), key=lambda x: x.lower()),
        "branch": sorted(list(set(c.branch for c in colleges if c.branch)), key=lambda x: x.lower())
    }
    logger.info(f"✅ Updated suggestions: {app.state.suggestions}")

# Create database tables and initialize data at startup
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        db = SessionLocal()
        try:
            clean_duplicates(db)
            normalize_case(db)
            db.execute("SELECT cutoff_min, cutoff_max FROM colleges LIMIT 1")
            logger.info("✅ Schema verified: 'cutoff_min' and 'cutoff_max' columns exist")
        except Exception as e:
            logger.error(f"❌ Schema verification failed: {e}")
        finally:
            db.close()
        initialize_database()
        db = SessionLocal()
        try:
            update_suggestions(db)
        finally:
            db.close()
        logger.info("✅ Database initialization completed")
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    try:
        query = db.query(College)
        colleges = get_deduplicated_colleges(query, db)
        logger.info(f"GET /: Found {len(colleges)} colleges in database")
        if not colleges:
            logger.warning("GET /: Warning: No colleges found in database!")
        else:
            logger.info(f"GET /: Colleges: {[c.name for c in colleges]}")

        results = format_college_results(colleges, db)
        suggestions = app.state.suggestions
        if not any(suggestions.values()):
            logger.error("GET /: Error: Suggestions are empty! Check database data.")

        states = sorted(set(c.state for c in colleges if c.state))
        locations = sorted(set(c.location for c in colleges if c.location))
        seo_metadata = {
            "title": "Find Top Colleges in India | BTech, Diploma, Degree",
            "description": f"Discover top colleges in {', '.join(states[:3]) + ' and more' if states else 'India'} for BTech, Diploma, and Degree courses.",
            "keywords": f"colleges in India, {', '.join(states)}, {', '.join(locations[:5])}, BTech colleges, Diploma colleges, Degree colleges",
            "og_title": "Best Colleges in India - Find Your Perfect Institute",
            "og_description": f"Explore colleges in {', '.join(states[:2]) + ' and other states' if states else 'India'} with detailed reviews and filters.",
            "og_url": str(request.url),
            "twitter_card": "summary_large_image"
        }

        context = {
            "request": request,
            "results": results,
            "suggestions": suggestions,
            "error": "No colleges found in database!" if not colleges else None,
            "form_data": {},
            "seo": seo_metadata,
            "use_table": len(results) > 5
        }
        logger.info(f"GET /: Context passed to template: {context}")
        return templates.TemplateResponse("index.html", context)

    except Exception as e:
        logger.error(f"❌ GET /: Error loading data: {e}")
        seo_metadata = {
            "title": "Find Colleges in India",
            "description": "Search for colleges in India by course, state, and more.",
            "keywords": "colleges, India, education",
            "og_title": "Find Colleges in India",
            "og_description": "Search for colleges in India.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
        context = {
            "request": request,
            "results": [],
            "suggestions": {"college_name": [], "location": [], "state": [], "branch": []},
            "error": f"Error loading colleges: {str(e)}",
            "form_data": {},
            "seo": seo_metadata,
            "use_table": False
        }
        return templates.TemplateResponse("index.html", context)

@app.head("/")
async def head_root():
    return Response(status_code=200)

@app.post("/", response_class=HTMLResponse)
async def index_post(
    request: Request,
    course_level: str = Form(...),
    state: Optional[str] = Form(default=""),
    location: Optional[str] = Form(default=""),
    college_name: Optional[str] = Form(default=""),
    branch: Optional[str] = Form(default=""),
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default=""),
    db: Session = Depends(get_db)
):
    try:
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
 upwards: 0.8
        college_name_lower = college_name.lower()
        if college_name_lower in {k.lower(): v for k, v in COLLEGE_MAPPINGS.items()}:
            college_name = COLLEGE_MAPPINGS[[k for k in COLLEGE_MAPPINGS if k.lower() == college_name_lower][0]]
        logger.info(f"POST /: Inputs - course_level: {course_level}, state: {state}, location: {location}, college_name: {college_name}, branch: {branch}, fees: {fees}, score: {score}")

        # Build query
        query = db.query(College).filter(College.course_level == course_level)
        if state:
            query = query.filter(College.state.ilike(state))
        if location:
            query = query.filter(College.location.ilike(location))
        if college_name:
            query = query.filter(College.name.ilike(college_name))
        if branch:
            query = query.filter(College.branch.ilike(branch))
        if fees:
            try:
                fees_value = float(fees)
                lower_fee = (fees_value // 100000) * 100000
                upper_fee = lower_fee + 100000
                query = query.filter(College.fees.between(lower_fee, upper_fee))
            except ValueError:
                logger.warning(f"POST /: Invalid fees input: {fees}")
        if score:
            try:
                score_value = float(score)
                query = query.filter(College.cutoff_min <= score_value, College.cutoff_max >= score_value)
            except ValueError:
                logger.warning(f"POST /: Invalid score input: {score}")

        colleges = get_deduplicated_colleges(query, db)
        logger.info(f"POST /: Query results count: {len(colleges)}")

        if not any([state, location, college_name, branch, fees, score]):
            colleges = get_deduplicated_colleges(db.query(College).filter(College.course_level == course_level), db)
            logger.info(f"POST /: All colleges for {course_level}: {len(colleges)}")

        results = format_college_results(colleges, db)
        suggestions = app.state.suggestions
        if not any(suggestions.values()):
            logger.error("POST /: Error: Suggestions are empty! Check database data.")

        error_message = None
        if not results:
            error_message = "No colleges found matching your criteria."
            if state and state not in suggestions["state"]:
                error_message = f"No colleges found for state '{state}'. Available states: {', '.join(suggestions['state'][:5])}"
            elif location and location not in suggestions["location"]:
                error_message = f"No colleges found for location '{location}'. Available locations: {', '.join(suggestions['location'][:5])}"
            elif college_name and college_name not in suggestions["college_name"]:
                error_message = f"No colleges found for college name '{college_name}'."
            elif branch and branch not in suggestions["branch"]:
                error_message = f"No colleges found for branch '{branch}'. Available branches: {', '.join(suggestions['branch'][:5])}"
            elif score and not score.replace(".", "").isdigit():
                error_message = f"Score '{score}' is invalid."

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
            "results": results,
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
        logger.info(f"POST /: Context passed to template: {context}")
        return templates.TemplateResponse("index.html", context)

    except Exception as e:
        logger.error(f"❌ POST /: Search error: {e}")
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
                "error": f"An error occurred while searching: {str(e)}",
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

@app.post("/api/search")
async def search(
    course_level: str = Form(...),
    state: Optional[str] = Form(default=""),
    location: Optional[str] = Form(default=""),
    college_name: Optional[str] = Form(default=""),
    branch: Optional[str] = Form(default=""),
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default=""),
    db: Session = Depends(get_db)
):
    try:
        if not course_level:
            return {"error": "Course level is required"}, 400
        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if course_level not in allowed_course_levels:
            return {"error": f"Course level must be one of {allowed_course_levels}"}, 400

        # Normalize inputs
        state = state.strip().title() if state else ""
        location = location.strip().title() if location else ""
        college_name = college_name.strip().title() if college_name else ""
        branch = branch.strip().title() if branch else ""

        # Apply college name mapping
        college_name_lower = college_name.lower()
        if college_name_lower in {k.lower(): v for k, v in COLLEGE_MAPPINGS.items()}:
            college_name = COLLEGE_MAPPINGS[[k for k in COLLEGE_MAPPINGS if k.lower() == college_name_lower][0]]

        query = db.query(College).filter(College.course_level == course_level)
        if state:
            query = query.filter(College.state.ilike(state))
        if location:
            query = query.filter(College.location.ilike(location))
        if college_name:
            query = query.filter(College.name.ilike(college_name))
        if branch:
            query = query.filter(College.branch.ilike(branch))
        if fees:
            try:
                max_fees = float(fees)
                query = query.filter(College.fees <= max_fees)
            except ValueError:
                logger.warning(f"POST /api/search: Invalid fees input: {fees}")
        if score:
            try:
                score_value = float(score)
                query = query.filter(College.cutoff_min <= score_value, College.cutoff_max >= score_value)
            except ValueError:
                logger.warning(f"POST /api/search: Invalid score input: {score}")

        colleges = get_deduplicated_colleges(query, db)
        results = format_college_results(colleges, db)
        suggestions = app.state.suggestions
        logger.info(f"POST /api/search: Found {len(results)} colleges, {len(suggestions)} suggestions")
        return {"results": results, "suggestions": suggestions}

    except Exception as e:
        logger.error(f"❌ POST /api/search: Error: {e}")
        return {"error": "An error occurred while searching"}, 500

@app.post("/api/submit_review")
async def submit_review(
    college_name: str = Form(...),
    review_text: str = Form(...),
    rating: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        if not college_name or not review_text or not rating:
            return {"error": "College name, review text, and rating are required"}, 400

        try:
            rating_value = float(rating)
            if not (1 <= rating_value <= 5):
                return {"error": "Rating must be between 1 and 5"}, 400
        except ValueError:
            return {"error": "Invalid rating format"}, 400

        college_name = college_name.strip().title()
        college = db.query(College).filter(College.name.ilike(college_name)).first()
        if not college:
            return {"error": "College not found"}, 404

        new_review = Review(
            college_name=college.name,
            review_text=review_text,
            rating=rating_value
        )
        db.add(new_review)
        db.commit()
        return {"message": "Review submitted successfully"}

    except Exception as e:
        logger.error(f"❌ Error submitting review: {e}")
        return {"error": f"Database error: {str(e)}"}, 500

@app.post("/add_college", response_class=HTMLResponse)
async def add_college(
    request: Request,
    name: str = Form(...),
    state: str = Form(...),
    location: str = Form(...),
    course_level: str = Form(...),
    branch: str = Form(...),
    fees: float = Form(...),
    cutoff_min: float = Form(...),
    cutoff_max: float = Form(...),
    review_text: Optional[str] = Form(default=""),
    rating: Optional[int] = Form(default=None),
    db: Session = Depends(get_db)
):
    try:
        if not all([name, state, location, course_level, branch, fees, cutoff_min, cutoff_max]):
            raise HTTPException(status_code=400, detail="All fields except review and rating are required.")

        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if course_level not in allowed_course_levels:
            raise HTTPException(status_code=400, detail=f"Course level must be one of {allowed_course_levels}.")

        allowed_branches = {
            "BTech": ["Mechanical Engineering", "Computer Science", "Civil Engineering", "Electronics and Telecommunication"],
            "Diploma": ["Mechanical Engineering", "Computer Science", "Civil Engineering", "Electronics and Telecommunication"],
            "Degree": ["Science", "Commerce", "Arts"]
        }
        if branch not in allowed_branches[course_level]:
            raise HTTPException(status_code=400, detail=f"Branch must be one of {allowed_branches[course_level]} for {course_level}.")

        if fees < 0:
            raise HTTPException(status_code=400, detail="Fees cannot be negative.")

        if cutoff_min < 0 or cutoff_max < 0:
            raise HTTPException(status_code=400, detail="Cutoff scores cannot be negative.")

        if cutoff_min > cutoff_max:
            raise HTTPException(status_code=400, detail="Cutoff min cannot be greater than cutoff max.")

        if rating and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

        name = name.strip().title()
        state = state.strip().title()
        location = location.strip().title()
        branch = branch.strip().title()

        if db.query(College).filter(College.name.ilike(name)).first():
            raise HTTPException(status_code=400, detail="College with this name already exists.")

        new_college = College(
            name=name,
            state=state,
            location=location,
            course_level=course_level,
            branch=branch,
            fees=fees,
            cutoff_min=cutoff_min,
            cutoff_max=cutoff_max
        )
        db.add(new_college)
        db.commit()

        if review_text and rating:
            new_review = Review(
                college_name=name,
                review_text=review_text,
                rating=rating
            )
            db.add(new_review)
            db.commit()

        update_suggestions(db)
        suggestions = app.state.suggestions

        seo_metadata = {
            "title": f"College Added - {name} in {state}",
            "description": f"Successfully added {name} in {location}, {state} offering {course_level} in {branch}.",
            "keywords": f"{name}, {state}, {location}, {course_level}, {branch}, college India",
            "og_title": f"New College: {name} in {state}",
            "og_description": f"Added {name} in {location}, {state} to our database.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": suggestions,
                "error": None,
                "form_data": {},
                "success_message": f"✅ College '{name}' added successfully!",
                "seo": seo_metadata,
                "use_table": False
            }
        )

    except Exception as e:
        logger.error(f"❌ Error adding college: {e}")
        seo_metadata = {
            "title": "Error - Add College",
            "description": "An error occurred while adding a college.",
            "keywords": "college, India",
            "og_title": "Error - Add College",
            "og_description": "An error occurred while adding a college.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": app.state.suggestions,
                "error": f"Error adding college: {str(e)}",
                "form_data": {},
                "seo": seo_metadata,
                "use_table": False
            }
        )

@app.get("/api/suggestions")
async def get_suggestions(db: Session = Depends(get_db)):
    try:
        return app.state.suggestions
    except Exception as e:
        logger.error(f"❌ GET /api/suggestions: Error: {e}")
        return {"college_name": [], "location": [], "state": [], "branch": []}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/colleges")
async def list_colleges(db: Session = Depends(get_db)):
    try:
        colleges = get_deduplicated_colleges(db.query(College), db)
        results = format_college_results(colleges, db)
        logger.info(f"GET /api/colleges: Found {len(results)} colleges")
        return results
    except Exception as e:
        logger.error(f"❌ GET /api/colleges: Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/predict_colleges/")
async def predict_colleges(score: int, db: Session = Depends(get_db)):
    try:
        if score < 0:
            raise HTTPException(status_code=400, detail="Score must be non-negative")
        query = db.query(College).filter(
            College.cutoff_min <= score,
            College.cutoff_max >= score
        )
        colleges = get_deduplicated_colleges(query, db)
        results = format_college_results(colleges, db)
        logger.info(f"GET /predict_colleges/?score={score}: Found {len(results)} colleges")
        return {"results": results}
    except Exception as e:
        logger.error(f"❌ GET /predict_colleges/: Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/api/results")
async def get_results(score: int, db: Session = Depends(get_db)):
    try:
        if score < 0:
            raise HTTPException(status_code=400, detail="Score must be non-negative")
        query = db.query(College).filter(
            College.cutoff_min <= score,
            College.cutoff_max >= score
        )
        colleges = get_deduplicated_colleges(query, db)
        results = format_college_results(colleges, db)
        suggestions = [
            {
                "name": c.name,
                "state": c.state,
                "location": c.location,
                "course_level": c.course_level,
                "branch": c.branch,
                "min_score": c.cutoff_min,
                "max_score": c.cutoff_max,
                "fees": c.fees
            } for c in colleges
        ]
        logger.info(f"GET /api/results?score={score}: Found {len(results)} colleges, {len(suggestions)} suggestions")
        return {"results": results, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"❌ GET /api/results: Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
