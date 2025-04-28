from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, Base
from models import College, Review
from typing import Optional
import os
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

# College name mappings to normalize user input
COLLEGE_MAPPINGS = {
    "tech college": "Tech College",
    "science college": "Science College",
    "eng college": "Engineering College",
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
        print(f"GET /: Found {len(colleges)} colleges in database")
        if not colleges:
            print("GET /: Warning: No colleges found in database!")
        else:
            print(f"GET /: Colleges: {[c.name for c in colleges]}")

        # Generate suggestions
        all_suggestions = {
            "college_name": sorted([c.name for c in colleges], key=str.lower),
            "location": sorted([c.location for c in colleges if c.location], key=str.lower),
            "state": sorted([c.state for c in colleges if c.state], key=str.lower)
        }
        print(f"GET /: Initial suggestions: {all_suggestions}")
        if not any(all_suggestions.values()):
            print("GET /: Error: Suggestions are empty! Check database data.")

    except Exception as e:
        print(f"❌ GET /: Error loading suggestions: {e}")
        all_suggestions = {"college_name": [], "location": [], "state": []}
    finally:
        db.close()

    context = {
        "request": request,
        "results": [],
        "suggestions": all_suggestions,
        "error": None,
        "form_data": {}
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
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default="")
):
    db = SessionLocal()
    try:
        # Validation
        if not course_level:
            raise HTTPException(status_code=400, detail="Course level is required.")

        # Normalize inputs
        state = state.strip() if state else ""
        location = location.strip() if location else ""
        college_name = college_name.strip() if college_name else ""

        # Apply college name mapping
        college_name_lower = college_name.lower()
        if college_name_lower in COLLEGE_MAPPINGS:
            college_name = COLLEGE_MAPPINGS[college_name_lower]
        print(f"POST /: Inputs - course_level: {course_level}, state: {state}, location: {location}, college_name: {college_name}, fees: {fees}, score: {score}")

        # Base query
        query = db.query(College).filter(
            College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
        )

        # Apply filters with case-insensitive prefix matching
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
                print(f"POST /: Invalid fees input: {fees}")
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
                print(f"POST /: Invalid score input: {score}")

        colleges = query.all()
        print(f"POST /: Query results count: {len(colleges)}")

        # If no optional filters, show all for the mandatory course_level
        if not any([state, location, college_name, fees, score]):
            colleges = db.query(College).filter(
                College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
            ).all()
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
                "course_level": "Undergraduate" if college.course_level == "UG" else "Postgraduate",
                "min_score": college.cutoff,
                "fees": college.fees,
                "avg_rating": avg_rating,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews[:2]]
            })

        # Generate autosuggestions based on user input prefixes
        all_colleges = db.query(College).all()
        existing_college_names = [c.name for c in all_colleges]
        existing_locations = [c.location for c in all_colleges if c.location]
        existing_states = [c.state for c in all_colleges if c.state]

        suggestions = {
            "college_name": sorted(
                [name for name in existing_college_names if name.lower().startswith(college_name.lower())],
                key=str.lower
            ) if college_name else sorted(existing_college_names, key=str.lower),
            "location": sorted(
                [loc for loc in existing_locations if loc.lower().startswith(location.lower())],
                key=str.lower
            ) if location else sorted(existing_locations, key=str.lower),
            "state": sorted(
                [st for st in existing_states if st.lower().startswith(state.lower())],
                key=str.lower
            ) if state else sorted(existing_states, key=str.lower)
        }
        print(f"POST /: Generated suggestions: {suggestions}")
        if not any(suggestions.values()):
            print("POST /: Error: Suggestions are empty! Check database data.")

        # Check for invalid inputs and provide specific error messages
        error_message = None
        if not results:
            if state and not any(st.lower().startswith(state.lower()) for st in existing_states):
                error_message = f"Result fetching error: No matching colleges found for state '{state}'."
            elif location and not any(loc.lower().startswith(location.lower()) for loc in existing_locations):
                error_message = f"Result fetching error: No matching colleges found for location '{location}'."
            elif college_name and not any(name.lower().startswith(college_name.lower()) for name in existing_college_names):
                error_message = f"Result fetching error: No matching colleges found for college name '{college_name}'."
            else:
                error_message = "No colleges found matching your criteria."

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
                "fees": fees,
                "score": score
            }
        }
        print(f"POST /: Context passed to template: {context}")
        return templates.TemplateResponse("index.html", context)

    except Exception as e:
        print(f"❌ POST /: Search error: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": {"college_name": [], "location": [], "state": []},
                "error": f"An error occurred while searching: {str(e)}",
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

@app.post("/api/search")
async def search(
    course_level: str = Form(...),
    state: Optional[str] = Form(default=""),
    location: Optional[str] = Form(default=""),
    college_name: Optional[str] = Form(default=""),
    fees: Optional[str] = Form(default=""),
    score: Optional[str] = Form(default="")
):
    db = SessionLocal()
    try:
        if not course_level:
            return {"error": "Course level is required"}, 400

        # Normalize inputs
        state = state.strip() if state else ""
        location = location.strip() if location else ""
        college_name = college_name.strip() if college_name else ""

        # Apply college name mapping
        if college_name.lower() in COLLEGE_MAPPINGS:
            college_name = COLLEGE_MAPPINGS[college_name.lower()]

        query = db.query(College).filter(
            College.course_level == ("UG" if course_level.lower() == "undergraduate" else "PG")
        )

        # Filters with prefix matching
        if state:
            query = query.filter(College.state.ilike(f"{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"{location}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"{college_name}%"))
        if fees:
            try:
                max_fees = float(fees)
                query = query.filter(College.fees <= max_fees)
            except ValueError:
                pass
        if score:
            try:
                min_score = float(score)
                query = query.filter(College.cutoff <= min_score)
            except ValueError:
                pass

        colleges = query.all()

        # Deduplicate colleges by name, state, location, course_level
        seen = set()
        deduplicated_colleges = []
        for college in colleges:
            key = (college.name, college.state, college.location, college.course_level)
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
                "course_level": "Undergraduate" if college.course_level == "UG" else "Postgraduate",
                "min_score": college.cutoff,
                "fees": college.fees,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews]
            })

        # Generate autosuggestions based on user input prefixes
        all_colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted(
                [c.name for c in all_colleges if c.name.lower().startswith(college_name.lower())],
                key=str.lower
            ) if college_name else sorted([c.name for c in all_colleges], key=str.lower),
            "location": sorted(
                [c.location for c in all_colleges if c.location and c.location.lower().startswith(location.lower())],
                key=str.lower
            ) if location else sorted([c.location for c in all_colleges if c.location], key=str.lower),
            "state": sorted(
                [c.state for c in all_colleges if c.state and c.state.lower().startswith(state.lower())],
                key=str.lower
            ) if state else sorted([c.state for c in all_colleges if c.state], key=str.lower)
        }

        return {"results": results, "suggestions": suggestions}

    except Exception as e:
        print(f"❌ API search error: {e}")
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
    fees: float = Form(...),
    cutoff: float = Form(...),
    review_text: Optional[str] = Form(default=""),
    rating: Optional[int] = Form(default=None)
):
    db = SessionLocal()
    try:
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
        if db.query(College).filter(College.name == name).first():
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
            "state": sorted([c.state for c in all_colleges if c.state], key=str.lower)
        }

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "results": [],
                "suggestions": suggestions,
                "error": None,
                "form_data": {},
                "success_message": f"✅ College '{name}' added successfully!"
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
@app.get("/api/suggestions")
async def get_suggestions():
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        suggestions = {
            "college_name": sorted([c.name for c in colleges], key=str.lower),
            "location": sorted([c.location for c in colleges if c.location], key=str.lower),
            "state": sorted([c.state for c in colleges if c.state], key=str.lower)
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
