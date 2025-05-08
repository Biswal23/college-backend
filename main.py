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
@app.on_event("startup")
async def startup_event():
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
    initialize_database()
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

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    colleges = db.query(College).all()
    print(f"DEBUG: Found {len(colleges)} colleges: {[c.name for c in colleges]}")
    
    suggestions = {
        "college_name": [c.name for c in db.query(College.name).distinct().all()],
        "state": [s.state for s in db.query(College.state).distinct().all()],
        "location": [l.location for l in db.query(College.location).distinct().all()],
        "branch": [b.branch for b in db.query(College.branch).distinct().all()]
    }
    
    context = {
        "request": request,
        "results": colleges,
        "suggestions": suggestions,
        "error": "No colleges found in database!" if not colleges else None,
        "form_data": {},
        "seo": {
            "title": "Find Top Colleges in India | BTech, Diploma, Degree",
            "description": "Discover top colleges in Delhi, Gujarat, Karnataka and more for BTech, Diploma, and Degree courses. Filter by state, district, fees, and cutoff scores.",
            "keywords": ", ".join([s for s in suggestions.state + suggestions.location + ["BTech colleges", "Diploma colleges", "Degree colleges"] if s]),
            "og_title": "Best Colleges in India - Find Your Perfect Institute",
            "og_description": "Explore colleges in Delhi, Gujarat and other states with detailed reviews and filters.",
            "og_url": "https://collegefilter.onrender.com/",
            "twitter_card": "summary_large_image"
        },
        "use_table": False
    }
    
    return templates.TemplateResponse("index.html", context)

    except Exception as e:
        print(f"❌ GET /: Error loading suggestions: {e}")
        all_suggestions = {"college_name": [], "location": [], "state": [], "branch": []}
        seo_metadata = {
            "title": "Find Colleges in India",
            "description": "Search for colleges in India by course, state, and more.",
            "keywords": "colleges, India, education",
            "og_title": "Find Colleges in India",
            "og_description": "Search for colleges in India.",
            "og_url": str(request.url),
            "twitter_card": "summary"
        }
    finally:
        db.close()

    context = {
        "request": request,
        "results": [],
        "suggestions": all_suggestions,
        "error": None,
        "form_data": {},
        "seo": seo_metadata,
        "use_table": False
    }
    print(f"GET /: Context passed to template: {context}")
    return templates.TemplateResponse("index.html", context)

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
        state = state.strip() if state else ""
        location = location.strip() if location else ""
        college_name = college_name.strip() if college_name else ""
        branch = branch.strip() if branch else ""

        # Apply college name mapping
        college_name_lower = college_name.lower()
        if college_name_lower in COLLEGE_MAPPINGS:
            college_name = COLLEGE_MAPPINGS[college_name_lower]
        print(f"POST /: Inputs - course_level: {course_level}, state: {state}, location: {location}, college_name: {college_name}, branch: {branch}, fees: {fees}, score: {score}")

        # Base query
        query = db.query(College).filter(College.course_level == course_level)

        # Apply filters with exact matching
        if state:
            query = query.filter(College.state == state)
        if location:
            query = query.filter(College.location == location)
        if college_name:
            query = query.filter(College.name == college_name)
        if branch:
            query = query.filter(College.branch == branch)
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

        # Generate autosuggestions based on exact matches
        all_colleges = db.query(College).all()
        existing_college_names = [c.name for c in all_colleges]
        existing_locations = [c.location for c in all_colleges if c.location]
        existing_states = [c.state for c in all_colleges if c.state]
        existing_branches = [c.branch for c in all_colleges if c.branch]

        suggestions = {
            "college_name": sorted(
                set(c.name for c in colleges if c.name and (not college_name or college_name == c.name)),
                key=lambda x: x.lower()
            ),
            "location": sorted(
                set(c.location for c in colleges if c.location and (not location or location == c.location)),
                key=lambda x: x.lower()
            ),
            "state": sorted(
                set(c.state for c in colleges if c.state and (not state or state == c.state)),
                key=lambda x: x.lower()
            ),
            "branch": sorted(
                set(c.branch for c in colleges if c.branch and (not branch or branch == c.branch)),
                key=lambda x: x.lower()
            )
        }
        print(f"POST /: Generated suggestions: {suggestions}")
        if not any(suggestions.values()):
            print("POST /: Error: Suggestions are empty! Check database data.")

        # Check for invalid inputs and provide specific error messages
        error_message = None
        if not results:
            if state and state not in existing_states:
                error_message = f"Result fetching error: No matching colleges found for state '{state}'."
            elif location and location not in existing_locations:
                error_message = f"Result fetching error: No matching colleges found for location '{location}'."
            elif college_name and college_name not in existing_college_names:
                error_message = f"Result fetching error: No matching colleges found for college name '{college_name}'."
            elif branch and branch not in existing_branches:
                error_message = f"Result fetching error: No matching colleges found for branch '{branch}'."
            elif score and not score.isdigit():
                error_message = f"Result fetching error: Score '{score}' is invalid."
            else:
                error_message = "No colleges found matching your criteria."

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
    finally:
        db.close()

@app.post("/api/search")
async def search(
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
        if not course_level:
            return {"error": "Course level is required"}, 400
        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if course_level not in allowed_course_levels:
            return {"error": f"Course level must be one of {allowed_course_levels}"}, 400

        # Normalize inputs
        state = state.strip() if state else ""
        location = location.strip() if location else ""
        college_name = college_name.strip() if college_name else ""
        branch = branch.strip() if branch else ""

        # Apply college name mapping
        if college_name.lower() in COLLEGE_MAPPINGS:
            college_name = COLLEGE_MAPPINGS[college_name.lower()]

        query = db.query(College).filter(College.course_level == course_level)

        # Filters with exact matching
        if state:
            query = query.filter(College.state == state)
        if location:
            query = query.filter(College.location == location)
        if college_name:
            query = query.filter(College.name == college_name)
        if branch:
            query = query.filter(College.branch == branch)
        if fees:
            try:
                max_fees = float(fees)
                query = query.filter(College.fees <= max_fees)
            except ValueError:
                print(f"POST /api/search: Invalid fees input: {fees}")
        if score:
            try:
                score_value = float(score)
                query = query.filter(College.cutoff_min <= score_value, College.cutoff_max >= score_value)
            except ValueError:
                print(f"POST /api/search: Invalid score input: {score}")

        colleges = query.all()

        # Deduplicate colleges
        seen = set()
        deduplicated_colleges = []
        for college in colleges:
            key = (college.name, college.state, college.location, college.course_level, college.branch)
            if key not in seen:
                seen.add(key)
                deduplicated_colleges.append(college)

        # Format results
        results = []
        for college in deduplicated_colleges:
            reviews = db.query(Review).filter(Review.college_name == college.name).all()
            results.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "branch": college.branch,
                "min_score": college.cutoff_min,
                "max_score": college.cutoff_max,
                "fees": college.fees,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews]
            })

        # Generate autosuggestions
        all_colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted(
                [c.name for c in all_colleges if not college_name or college_name == c.name],
                key=str.lower
            ),
            "location": sorted(
                [c.location for c in all_colleges if c.location and (not location or location == c.location)],
                key=str.lower
            ),
            "state": sorted(
                [c.state for c in all_colleges if c.state and (not state or state == c.state)],
                key=str.lower
            ),
            "branch": sorted(
                [c.branch for c in all_colleges if c.branch and (not branch or branch == c.branch)],
                key=str.lower
            )
        }

        return {"results": results, "suggestions": suggestions}

    except Exception as e:
        print(f"❌ POST /api/search: Error: {e}")
        return {"error": "An error occurred while searching"}, 500
    finally:
        db.close()

@app.post("/api/submit_review")
async def submit_review(
    college_name: str = Form(...),
    review_text: str = Form(...),
    rating: str = Form(...)
):
    db = SessionLocal()
    try:
        if not college_name or not review_text or not rating:
            return {"error": "College name, review text, and rating are required"}, 400

        try:
            rating_value = float(rating)
            if not (1 <= rating_value <= 5):
                return {"error": "Rating must be between 1 and 5"}, 400
        except ValueError:
            return {"error": "Invalid rating format"}, 400

        # Check if college exists
        college = db.query(College).filter(College.name == college_name).first()
        if not college:
            return {"error": "College not found"}, 404

        # Add review
        new_review = Review(
            college_name=college_name,
            review_text=review_text,
            rating=rating_value
        )
        db.add(new_review)
        db.commit()

        return {"message": "Review submitted successfully"}

    except Exception as e:
        print(f"❌ Error submitting review: {e}")
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        db.close()

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
    rating: Optional[int] = Form(default=None)
):
    db = SessionLocal()
    try:
        if not all([name, state, location, course_level, branch, fees, cutoff_min, cutoff_max]):
            raise HTTPException(status_code=400, detail="All fields except review and rating are required.")

        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if course_level not in allowed_course_levels:
            raise HTTPException(status_code=400, detail=f"Course level must be one of {allowed_course_levels}.")

        # Validate branch based on course_level
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

        # Check if college exists
        if db.query(College).filter(College.name == name).first():
            raise HTTPException(status_code=400, detail="College with this name already exists.")

        # Create new college
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

        # Add review if given
        if review_text and rating:
            new_review = Review(
                college_name=name,
                review_text=review_text,
                rating=rating
            )
            db.add(new_review)
            db.commit()

        # Generate updated suggestions
        all_colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted([c.name for c in all_colleges], key=str.lower),
            "location": sorted([c.location for c in all_colleges if c.location], key=str.lower),
            "state": sorted([c.state for c in all_colleges if c.state], key=str.lower),
            "branch": sorted([c.branch for c in all_colleges if c.branch], key=str.lower)
        }

        # SEO metadata
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
        print(f"❌ Error adding college: {e}")
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
                "suggestions": {"college_name": [], "location": [], "state": [], "branch": []},
                "error": f"Error adding college: {str(e)}",
                "form_data": {},
                "seo": seo_metadata,
                "use_table": False
            }
        )
    finally:
        db.close()

@app.get("/api/suggestions")
async def get_suggestions():
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted([c.name for c in colleges], key=str.lower),
            "location": sorted([c.location for c in colleges if c.location], key=str.lower),
            "state": sorted([c.state for c in colleges if c.state], key=str.lower),
            "branch": sorted([c.branch for c in colleges if c.branch], key=str.lower)
        }
        return suggestions
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/colleges")
def list_colleges():
    db = SessionLocal()
    colleges = db.query(College).all()
    db.close()
    return colleges

@app.get("/predict_colleges/")
async def predict_colleges(score: int, db: Session = Depends(get_db)):
    try:
        # Validate score
        if score < 0:
            raise HTTPException(status_code=400, detail="Score must be non-negative")

        # Query colleges where score is within cutoff_min and cutoff_max
        colleges = db.query(College).filter(
            College.cutoff_min <= score,
            College.cutoff_max >= score
        ).all()

        # Format results to match other endpoints
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

        print(f"GET /predict_colleges/?score={score}: Found {len(results)} colleges")
        return {"results": sorted(results, key=lambda x: (-x["avg_rating"], x["fees"]))}

    except Exception as e:
        print(f"❌ GET /predict_colleges/: Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/api/results")
async def get_results(score: int, db: Session = Depends(get_db)):
    try:
        # Validate score
        if score < 0:
            raise HTTPException(status_code=400, detail="Score must be non-negative")

        # Query colleges where score is within cutoff_min and cutoff_max
        colleges = db.query(College).filter(
            College.cutoff_min <= score,
            College.cutoff_max >= score
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
                "course_level": college.course_level,
                "branch": college.branch,
                "min_score": college.cutoff_min,
                "max_score": college.cutoff_max,
                "fees": college.fees,
                "avg_rating": avg_rating,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews[:2]]
            })

        # Generate suggestions (all colleges for simplicity, could filter by proximity to score)
        all_colleges = db.query(College).all()
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
            } for c in all_colleges
        ]

        print(f"GET /api/results?score={score}: Found {len(results)} colleges, {len(suggestions)} suggestions")
        return {"results": sorted(results, key=lambda x: (-x["avg_rating"], x["fees"])), "suggestions": suggestions}

    except Exception as e:
        print(f"❌ GET /api/results: Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    initialize_database()

