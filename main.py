from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, engine
from models import Base, College, CollegeBranch, Review
import initial_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic models for request/response
class ReviewCreate(BaseModel):
    college_name: str
    review_text: str
    rating: float

class CollegeCreate(BaseModel):
    name: str
    state: str
    location: str
    course_level: str
    fees: float
    cutoff_min: float
    cutoff_max: float
    branches: List[str]

class CollegeResponse(BaseModel):
    name: str
    state: str
    location: str
    course_level: str
    fees: float
    cutoff_min: float
    cutoff_max: float
    branches: List[str]

class ReviewResponse(BaseModel):
    college_name: str
    review_text: str
    rating: float

# HTML for the frontend
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>College Database</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .section { margin-bottom: 20px; }
            .error { color: red; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            input { margin: 5px; padding: 5px; }
            button { padding: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>College Database</h1>

        <div class="section">
            <h2>Upload Excel File</h2>
            <input type="file" id="excelFile" accept=".xlsx">
            <button onclick="uploadExcel()">Upload</button>
            <p id="uploadMessage"></p>
        </div>

        <div class="section">
            <h2>Add College</h2>
            <input type="text" id="name" placeholder="College Name" required>
            <input type="text" id="state" placeholder="State" required>
            <input type="text" id="location" placeholder="Location" required>
            <input type="text" id="courseLevel" placeholder="Course Level (BTech/Diploma/Degree)" required>
            <input type="text" id="branches" placeholder="Branches (comma-separated)" required>
            <input type="number" id="fees" placeholder="Fees" step="0.01" required>
            <input type="number" id="cutoffMin" placeholder="Cutoff Rank (Min)" step="0.01" required>
            <input type="number" id="cutoffMax" placeholder="Cutoff Rank (Max)" step="0.01" required>
            <button onclick="addCollege()">Add College</button>
            <p id="addMessage"></p>
        </div>

        <div class="section">
            <h2>Search Colleges</h2>
            <input type="text" id="searchQuery" placeholder="Search by name, state, location, course level, or branches">
            <button onclick="searchColleges()">Search</button>
            <table id="collegeTable">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>State</th>
                        <th>Location</th>
                        <th>Course Level</th>
                        <th>Branches</th>
                        <th>Fees</th>
                        <th>Cutoff Rank (Min)</th>
                        <th>Cutoff Rank (Max)</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <script>
            async function uploadExcel() {
                const fileInput = document.getElementById('excelFile');
                const message = document.getElementById('uploadMessage');
                if (!fileInput.files.length) {
                    message.innerHTML = '<span class="error">Please select a file.</span>';
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                try {
                    const response = await fetch('/api/upload_excel', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    if (response.ok) {
                        message.innerHTML = `Successfully uploaded! ${result.summary.inserted_colleges} colleges inserted, ${result.summary.inserted_branches} branches inserted, ${result.summary.inserted_reviews} reviews inserted.`;
                    } else {
                        message.innerHTML = `<span class="error">Error: ${result.detail}</span>`;
                    }
                } catch (error) {
                    message.innerHTML = `<span class="error">Error uploading file: ${error.message}</span>`;
                }
            }

            async function addCollege() {
                const name = document.getElementById('name').value;
                const state = document.getElementById('state').value;
                const location = document.getElementById('location').value;
                const courseLevel = document.getElementById('courseLevel').value;
                const branches = document.getElementById('branches').value.split(',').map(b => b.trim()).filter(b => b);
                const fees = parseFloat(document.getElementById('fees').value);
                const cutoffMin = parseFloat(document.getElementById('cutoffMin').value);
                const cutoffMax = parseFloat(document.getElementById('cutoffMax').value);
                const message = document.getElementById('addMessage');

                // Client-side validation
                if (!name || !state || !location || !courseLevel || !branches.length) {
                    message.innerHTML = '<span class="error">All fields are required.</span>';
                    return;
                }
                if (isNaN(fees) || isNaN(cutoffMin) || isNaN(cutoffMax)) {
                    message.innerHTML = '<span class="error">Fees, Cutoff Rank (Min), and Cutoff Rank (Max) must be valid numbers.</span>';
                    return;
                }
                if (fees < 0 || cutoffMin < 0 || cutoffMax < 0) {
                    message.innerHTML = '<span class="error">Fees, Cutoff Rank (Min), and Cutoff Rank (Max) must be non-negative.</span>';
                    return;
                }
                if (cutoffMin > cutoffMax) {
                    message.innerHTML = '<span class="error">Cutoff Rank (Min) must be less than or equal to Cutoff Rank (Max).</span>';
                    return;
                }

                try {
                    const response = await fetch('/api/colleges', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name, state, location, course_level: courseLevel,
                            branches, fees, cutoff_min: cutoffMin, cutoff_max: cutoffMax
                        })
                    });
                    const result = await response.json();
                    if (response.ok) {
                        message.innerHTML = 'College added successfully!';
                        // Clear form
                        document.getElementById('name').value = '';
                        document.getElementById('state').value = '';
                        document.getElementById('location').value = '';
                        document.getElementById('courseLevel').value = '';
                        document.getElementById('branches').value = '';
                        document.getElementById('fees').value = '';
                        document.getElementById('cutoffMin').value = '';
                        document.getElementById('cutoffMax').value = '';
                    } else {
                        message.innerHTML = `<span class="error">Error: ${result.detail}</span>`;
                    }
                } catch (error) {
                    message.innerHTML = `<span class="error">Error adding college: ${error.message}</span>`;
                }
            }

            async function searchColleges() {
                const query = document.getElementById('searchQuery').value;
                const tbody = document.querySelector('#collegeTable tbody');
                tbody.innerHTML = '';

                try {
                    const response = await fetch(`/api/colleges/search?query=${encodeURIComponent(query)}`);
                    const colleges = await response.json();
                    if (response.ok) {
                        colleges.forEach(college => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${college.name}</td>
                                <td>${college.state}</td>
                                <td>${college.location}</td>
                                <td>${college.course_level}</td>
                                <td>${college.branches.join(', ')}</td>
                                <td>${college.fees}</td>
                                <td>${college.cutoff_min}</td>
                                <td>${college.cutoff_max}</td>
                            `;
                            tbody.appendChild(row);
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="8" class="error">Error fetching colleges.</td></tr>';
                    }
                } catch (error) {
                    tbody.innerHTML = `<tr><td colspan="8" class="error">Error: ${error.message}</td></tr>`;
                }
            }
        </script>
    </body>
    </html>
    """

# API Endpoints
@app.post("/api/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")
    try:
        content = await file.read()
        result = initial_data.process_excel_file(content)
        return {"message": "Excel file processed successfully", "data": result}
    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/colleges", response_model=List[CollegeResponse])
def get_colleges():
    db = SessionLocal()
    try:
        colleges = db.query(College).all()
        result = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            result.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "fees": college.fees,
                "cutoff_min": college.cutoff_min,
                "cutoff_max": college.cutoff_max,
                "branches": branches
            })
        return result
    finally:
        db.close()

@app.get("/api/colleges/search", response_model=List[CollegeResponse])
def search_colleges(query: Optional[str] = None):
    db = SessionLocal()
    try:
        if not query:
            colleges = db.query(College).all()
        else:
            query_lower = query.lower()
            # Search in College table
            colleges = db.query(College).filter(
                (College.name.ilike(f"%{query_lower}%")) |
                (College.state.ilike(f"%{query_lower}%")) |
                (College.location.ilike(f"%{query_lower}%")) |
                (College.course_level.ilike(f"%{query_lower}%"))
            ).all()

            # Search in CollegeBranch table
            branch_matches = db.query(CollegeBranch).filter(
                CollegeBranch.branch.ilike(f"%{query_lower}%")
            ).all()
            branch_college_names = {branch.college_name for branch in branch_matches}
            branch_colleges = db.query(College).filter(College.name.in_(branch_college_names)).all()

            # Combine results and remove duplicates
            college_names = {college.name for college in colleges}
            college_names.update(branch_college_names)
            colleges = db.query(College).filter(College.name.in_(college_names)).all()

        result = []
        for college in colleges:
            branches = [branch.branch for branch in college.branches]
            result.append({
                "name": college.name,
                "state": college.state,
                "location": college.location,
                "course_level": college.course_level,
                "fees": college.fees,
                "cutoff_min": college.cutoff_min,
                "cutoff_max": college.cutoff_max,
                "branches": branches
            })
        return result
    finally:
        db.close()

@app.post("/api/colleges", response_model=CollegeResponse)
def add_college(college: CollegeCreate):
    db = SessionLocal()
    try:
        # Validate course_level
        allowed_course_levels = ["BTech", "Diploma", "Degree"]
        if college.course_level not in allowed_course_levels:
            raise HTTPException(status_code=400, detail=f"Invalid course_level. Must be one of {allowed_course_levels}")

        # Validate branches
        allowed_branches = {
            "BTech": [
                "Mechanical Engineering", "Computer Science", "Civil Engineering", 
                "Electronics and Telecommunication", "Electrical Engineering",
                "Computer Science and Engineering", "Chemical Engineering",
                "Metallurgical and Materials Engineering", "Production Engineering",
                "Electrical and Electronics Engineering", "Information Technology",
                "Electronics & Communication Engineering", "Textile Engineering",
                "Bio Technology", "Fashion & Apparel Technology", 
                "Electronics & Instrumentation Engineering", "Plastic Engineering",
                "Manufacturing Engineering & Technology", "Automobile Engineering",
                "Mining Engineering", "Mineral Engineering", "Aeronautical Engineering",
                "Computer Engineering", "Computer Science & Technology",
                "Computer Science and Information Technology",
                "Computer Science Engineering (Artificial Intelligence and Machine Learning)",
                "Computer Science & Engineering (Data Science)",
                "Computer Science & Engineering (IoT and Cyber Security Including block chain technology)",
                "Electrical and Computer Engineering", "Electronics and Computer Engineering",
                "Agriculture Engineering", "Applied Electronics & Instrumentation",
                "Integrated M.Sc. in Material Science and Engg",
                "Integrated MSc in Applied Chemistry", "Integrated MSc in Applied Physics",
                "Integrated MSc in Mathematics and Computing", "B ARCH", "B. PLAN"
            ],
            "Diploma": ["Mechanical Engineering", "Computer Science", "Civil Engineering", 
                        "Electronics and Telecommunication"],
            "Degree": ["Science", "Commerce", "Arts", 
                       "B. Tech in Civil Engineering & M.Tech in Structural Engineering",
                       "B. Tech in Electrical Engineering & M.Tech in Power System Engineering"]
        }
        invalid_branches = [b for b in college.branches if b not in allowed_branches.get(college.course_level, [])]
        if invalid_branches:
            raise HTTPException(status_code=400, detail=f"Invalid branches for {college.course_level}: {invalid_branches}")

        # Validate numerical fields
        if college.fees < 0 or college.cutoff_min < 0 or college.cutoff_max < 0:
            raise HTTPException(status_code=400, detail="Fees, cutoff_min, and cutoff_max must be non-negative")
        if college.cutoff_min > college.cutoff_max:
            raise HTTPException(status_code=400, detail="cutoff_min must be less than or equal to cutoff_max")

        # Check if college exists
        existing_college = db.query(College).filter(College.name == college.name).first()
        if existing_college:
            raise HTTPException(status_code=400, detail="College already exists")

        # Create college
        db_college = College(
            name=college.name,
            state=college.state,
            location=college.location,
            course_level=college.course_level,
            fees=college.fees,
            cutoff_min=college.cutoff_min,
            cutoff_max=college.cutoff_max
        )
        db.add(db_college)

        # Add branches
        for branch in college.branches:
            db_branch = CollegeBranch(college_name=college.name, branch=branch)
            db.add(db_branch)

        db.commit()
        return {
            "name": db_college.name,
            "state": db_college.state,
            "location": db_college.location,
            "course_level": db_college.course_level,
            "fees": db_college.fees,
            "cutoff_min": db_college.cutoff_min,
            "cutoff_max": db_college.cutoff_max,
            "branches": college.branches
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/reviews", response_model=ReviewResponse)
def add_review(review: ReviewCreate):
    db = SessionLocal()
    try:
        if not (1 <= review.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        # Check if college exists
        college = db.query(College).filter(College.name == review.college_name).first()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")

        db_review = Review(
            college_name=review.college_name,
            review_text=review.review_text,
            rating=review.rating
        )
        db.add(db_review)
        db.commit()
        return {
            "college_name": db_review.college_name,
            "review_text": db_review.review_text,
            "rating": db_review.rating
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
