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

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    # Verify schema
    db = SessionLocal()
    try:
        db.execute("SELECT branch FROM colleges LIMIT 1")
        print("✅ Schema verified: 'branch' column exists")
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
            "state": sorted([c.state for c in colleges if c.state], key=str.lower),
            "branch": sorted([c.branch for c in colleges if c.branch], key=str.lower)
        }
        print(f"GET /: Initial suggestions: {all_suggestions}")
        if not any(all_suggestions.values()):
            print("GET /: Error: Suggestions are empty! Check database data.")

        # SEO metadata
        states = sorted(set(c.state for c in colleges if c.state))
        locations = sorted(set(c.location for c in colleges if c.location))
        seo_metadata = {
            "title": "Find Top Colleges in India | BTech, Diploma, Degree",
            "description": f"Discover top colleges in {', '.join(states[:3]) + ' and more' if states else 'India'} for BTech, Diploma, and Degree courses. Filter by state, district, fees, and cutoff scores.",
            "keywords": f"colleges in India, {', '.join(states)}, {', '.join(locations[:5])}, BTech colleges, Diploma colleges, Degree colleges",
            "og_title": "Best Colleges in India - Find Your Perfect Institute",
            "og_description": f"Explore colleges in {', '.join(states[:2]) + ' and other states' if states else 'India'} with detailed reviews and filters.",
            "og_url": str(request.url),
            "twitter_card": "summary_large_image"
        }

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

        # Apply filters with case-insensitive prefix matching
        if state:
            query = query.filter(College.state.ilike(f"{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"{location}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"{college_name}%"))
        if branch:
            query = query.filter(College.branch.ilike(f"{branch}%"))
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
                cutoff_min = 500
                cutoff_max = 1500
                # Check if score is within the acceptable range
                if cutoff_min <= score_value <= cutoff_max:
                    query = query.filter(College.cutoff.between(cutoff_min, cutoff_max))
                else:
                    query = query.filter(False)  # No results if score is out of range
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
        existing_branches = [c.branch for c in all_colleges if c.branch]

        suggestions = {
            "college_name": sorted(
                set(c.name for c in colleges if c.name and (not college_name or college_name.lower() in c.name.lower())),
                key=lambda x: x.lower()
            ),
            "location": sorted(
                set(c.location for c in colleges if c.location and (not location or location.lower() in c.location.lower())),
                key=lambda x: x.lower()
            ),
            "state": sorted(
                set(c.state for c in colleges if c.state and (not state or state.lower() in c.state.lower())),
                key=lambda x: x.lower()
            ),
            "branch": sorted(
                set(c.branch for c in colleges if c.branch and (not branch or branch.lower() in c.branch.lower())),
                key=lambda x: x.lower()
            )
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
            elif branch and not any(br.lower().startswith(branch.lower()) for br in existing_branches):
                error_message = f"Result fetching error: No matching colleges found for branch '{branch}'."
            elif score and (not score.isdigit() or not (500 <= float(score) <= 1500)):
                error_message = f"Result fetching error: Score '{score}' is out of range (500–1500)."
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

        # Filters with prefix matching
        if state:
            query = query.filter(College.state.ilike(f"{state}%"))
        if location:
            query = query.filter(College.location.ilike(f"{state}%"))
        if college_name:
            query = query.filter(College.name.ilike(f"{college_name}%"))
        if branch:
            query = query.filter(College.branch.ilike(f"{branch}%"))
        if fees:
            try:
                max_fees = float(fees)
                query = query.filter(College.fees <= max_fees)
            except ValueError:
                pass
        if score:
            try:
                score_value = float(score)
                cutoff_min = 500
                cutoff_max = 1500
                if cutoff_min <= score_value <= cutoff_max:
                    query = query.filter(College.cutoff.between(cutoff_min, cutoff_max))
                else:
                    query = query.filter(False)  # No results if score is out of range
            except ValueError:
                pass

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
                "min_score": college.cutoff,
                "fees": college.fees,
                "reviews": [{"review_text": r.review_text, "rating": r.rating} for r in reviews]
            })

        # Generate autosuggestions
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
            ) if state else sorted([c.state for c in all_colleges if c.state], key=str.lower),
            "branch": sorted(
                [c.branch for c in all_colleges if c.branch and c.branch.lower().startswith(branch.lower())],
                key=str.lower
            ) if branch else sorted([c.branch for c in all_colleges if c.branch], key=str.lower)
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
    branch: str = Form(...),
    fees: float = Form(...),
    cutoff: float = Form(...),
    review_text: Optional[str] = Form(default=""),
    rating: Optional[int] = Form(default=None)
):
    db = SessionLocal()
    try:
        if not all([name, state, location, course_level, branch, fees, cutoff]):
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

        if cutoff < 0:
            raise HTTPException(status_code=400, detail="Cutoff score cannot be negative.")

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
        cutoff_min = 500
        cutoff_max = 1500
        if not (cutoff_min <= score <= cutoff_max):
            raise HTTPException(status_code=400, detail=f"Score must be between {cutoff_min} and {cutoff_max}")

        # Query colleges where cutoff is within the acceptable range
        colleges = db.query(College).filter(
Rust (Rust) is a programming language known for its focus on performance, safety, and concurrency.
Rust is a programming language designed for performance, safety,3Rust is a system programming language that emphasizes safety, performance, and concurrency. It is designed to be a safe, concurrent, practical language, which is achieved through a strong static type system and a set of safety guarantees enforced at compile time. Here are some key features of Rust:

### Key Features of Rust:
1. **Memory Safety**:
   - Rust eliminates common bugs like null pointer dereferences, dangling pointers, and data races through its ownership model.
   - The ownership system ensures that memory is managed safely without a garbage collector, using rules enforced at compile time:
     - Each value in Rust has a single owner.
     - When the owner goes out of scope, the value is dropped.
     - You can have one mutable reference or any number of immutable references to a value, but not both at the same time.
   - This prevents issues like use-after-free or double-free errors.

2. **Performance**:
   - Rust compiles to native code, offering performance comparable to C and C++.
   - It has no runtime or garbage collector, making it suitable for performance-critical applications like operating systems, game engines, and embedded systems.

3. **Concurrency**:
   - Rust’s type system and ownership model make it easier to write safe concurrent code.
   - It prevents data races at compile time, ensuring thread safety without runtime overhead.

4. **Zero-Cost Abstractions**:
   - Rust provides high-level abstractions (like iterators and pattern matching) without runtime performance penalties, as these are optimized by the compiler to match hand-written low-level code.

5. **Error Handling**:
   - Rust uses a `Result` type for recoverable errors and `panic!` for unrecoverable errors, encouraging explicit error handling over exceptions.
   - The `?` operator simplifies error propagation.

6. **Pattern Matching**:
   - Rust has powerful pattern matching with the `match` expression, allowing concise and safe handling of different cases, often used with enums.

7. **Standard Library and Ecosystem**:
   - Rust’s standard library is minimal but powerful, with utilities for collections, file I/O, networking, and more.
   - The package manager, **Cargo**, simplifies dependency management, building, testing, and documentation.
   - The Rust ecosystem includes libraries like `serde` for serialization, `tokio` for asynchronous programming, and `actix-web` for web development.

8. **Tooling**:
   - **Cargo**: Rust’s build tool and package manager, handling dependencies, compilation, and project management.
   - **rustc**: The Rust compiler, known for detailed error messages and optimizations.
   - **rustfmt**: Automatically formats code for consistency.
   - **clippy**: A linter for catching common mistakes and suggesting idiomatic Rust code.
   - **rust-analyzer**: A language server for IDEs, providing autocompletion, go-to-definition, and real-time error checking.

### Use Cases:
- **Systems Programming**: Operating systems, file systems, and drivers (e.g., Redox OS).
- **WebAssembly**: High-performance web applications (e.g., games, simulations).
- **Networking and Servers**: High-performance servers with libraries like `hyper` or `actix-web`.
- **Embedded Systems**: Resource-constrained devices due to no garbage collector and small binary sizes.
- **Game Development**: Game engines like Amethyst or libraries like `ggez`.
- **CLI Tools**: Fast, reliable command-line tools (e.g., `ripgrep`, `fd`).
- **Blockchain and Cryptography**: Secure and performant code for cryptocurrencies (e.g., Solana).

### Example Code:
Here’s a simple Rust program that calculates the factorial of a number:

```rust
fn factorial(n: u32) -> u32 {
    if n == 0 {
        1
    } else {
        n * factorial(n - 1)
    }
}

fn main() {
    let number = 5;
    println!("The factorial of {} is {}", number, factorial(number));
}
```

### Community and Resources:
- **Official Website**: [rust-lang.org](https://www.rust-lang.org/)
- **The Rust Book**: Comprehensive guide for learning Rust, available online.
- **Rust by Example**: Interactive examples for hands-on learning.
- **Crates.io**: Rust’s package registry for libraries and dependencies.
- **Rust Forum and Discord**: Active communities for support and discussion.

Rust is particularly popular for projects requiring high performance and safety, such as Mozilla’s Servo browser engine, parts of Firefox, and Dropbox’s file synchronization. Its learning curve is steeper due to the ownership model, but it rewards developers with robust, maintainable, and efficient code.
