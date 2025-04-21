from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app,
     resources={
         r"/api/*": {
             "origins": [
                 "https://karamcollegeinfo.com",
                 "https://indian.karamcollegeinfo.com"
             ]
         }
     })  # Replace with your Hostinger domain


# Function to load college data and reviews from SQLite
def load_college_data():
    try:
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        # Load colleges
        cursor.execute(
            "SELECT name, state, location, course_level, cutoff, fees FROM colleges"
        )
        college_rows = cursor.fetchall()

        # Load reviews
        cursor.execute("SELECT college_name, review_text, rating FROM reviews")
        review_rows = cursor.fetchall()

        conn.close()

        # Map colleges to dictionary format with deduplication by name, state, location, course_level
        colleges_dict = {}
        for row in college_rows:
            key = (row[0], row[1], row[2], row[3]
                   )  # Unique key: (name, state, location, course_level)
            if key not in colleges_dict:
                colleges_dict[key] = {
                    "name": row[0],
                    "state": row[1],
                    "location": row[2],
                    "course_level":
                    "Undergraduate" if row[3] == "UG" else "Postgraduate",
                    "min_score": float(row[4]),
                    "fees": float(row[5]),
                    "reviews": []
                }

        colleges = list(colleges_dict.values())

        # Attach reviews to corresponding colleges
        for review in review_rows:
            college_name = review[0]
            for college in colleges:
                if college["name"] == college_name:
                    college["reviews"].append({
                        "review_text": review[1],
                        "rating": float(review[2])
                    })

        return colleges
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


# Web route for testing (optional, for Replit’s UI)
@app.route("/", methods=["GET", "POST"])
def index():
    colleges = load_college_data()
    locations = sorted(set(c["location"] for c in colleges if c["location"]))
    college_names = sorted(set(c["name"] for c in colleges if c["name"]))
    states = sorted(set(c["state"] for c in colleges if c["state"]))
    suggestions = {
        "college_name": college_names,
        "location": locations,
        "state": states
    }
    results = []
    error = None

    if request.method == "POST":
        course_level = request.form.get("course_level")
        state = request.form.get("state", "").strip()
        location = request.form.get("location", "").strip()
        college_name = request.form.get("college_name", "").strip()
        fees = request.form.get("fees", "")
        score = request.form.get("score", "")

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
                filtered = [
                    c for c in filtered
                    if location.lower() in c["location"].lower()
                ]
            if college_name:
                filtered = [
                    c for c in filtered
                    if college_name.lower() in c["name"].lower()
                ]
            if fees:
                try:
                    max_fees = float(fees)
                    filtered = [c for c in filtered if c["fees"] <= max_fees]
                except ValueError:
                    pass
            if score:
                try:
                    min_score = float(score)
                    filtered = [
                        c for c in filtered if c["min_score"] <= min_score
                    ]
                except ValueError:
                    pass
            # Deduplicate results by name, state, location, course_level
            seen = set()
            results = [
                x for x in filtered
                if not ((x["name"], x["state"], x["location"],
                         x["course_level"]) in seen or seen.add(
                             (x["name"], x["state"], x["location"],
                              x["course_level"])))
            ]

            if college_name:
                suggestions["college_name"] = [
                    n for n in college_names
                    if college_name.lower() in n.lower()
                ]
            if location:
                suggestions["location"] = [
                    l for l in locations if location.lower() in l.lower()
                ]
            if state:
                suggestions["state"] = [
                    s for s in states if state.lower() in s.lower()
                ]

    return render_template("index.html",
                           results=results,
                           suggestions=suggestions,
                           error=error)


# API route for Hostinger frontend
@app.route("/api/search", methods=["POST"])
def search():
    colleges = load_college_data()
    course_level = request.form.get("course_level", "").strip()
    state = request.form.get("state", "").strip()
    location = request.form.get("location", "").strip()
    college_name = request.form.get("college_name", "").strip()
    fees = request.form.get("fees", "")
    score = request.form.get("score", "")

    if not course_level or not state:
        return jsonify({"error": "Course level and state are required"}), 400

    filtered = colleges
    filtered = [
        c for c in filtered
        if c["course_level"].lower() == course_level.lower()
        and c["state"].lower() == state.lower()
    ]
    if location:
        filtered = [
            c for c in filtered if location.lower() in c["location"].lower()
        ]
    if college_name:
        filtered = [
            c for c in filtered if college_name.lower() in c["name"].lower()
        ]
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
    # Deduplicate results by name, state, location, course_level
    seen = set()
    results = [
        x for x in filtered
        if not ((x["name"], x["state"], x["location"],
                 x["course_level"]) in seen or seen.add((
                     x["name"], x["state"], x["location"], x["course_level"])))
    ]
    # Return suggestions for college_name, location, and state
    suggestions = {
        "college_name":
        sorted(set(c["name"] for c in colleges if c["name"] and (
            not college_name or college_name.lower() in c["name"].lower())),
               key=lambda x: x.lower()),
        "location":
        sorted(set(c["location"] for c in colleges if c["location"] and (
            not location or location.lower() in c["location"].lower())),
               key=lambda x: x.lower()),
        "state":
        sorted(set(c["state"] for c in colleges if c["state"] and (
            not state or state.lower() in c["state"].lower())),
               key=lambda x: x.lower())
    }

    return jsonify({"results": results, "suggestions": suggestions})


# Optional: Endpoint to submit a review
@app.route("/api/submit_review", methods=["POST"])
def submit_review():
    college_name = request.form.get("college_name", "").strip()
    review_text = request.form.get("review_text", "").strip()
    rating = request.form.get("rating", "")

    if not college_name or not review_text or not rating:
        return jsonify(
            {"error":
             "College name, review text, and rating are required"}), 400

    try:
        rating = float(rating)
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except ValueError:
        return jsonify({"error": "Invalid rating format"}), 400

    try:
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM colleges WHERE name = ?",
                       (college_name, ))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "College not found"}), 404
        cursor.execute(
            "INSERT INTO reviews (college_name, review_text, rating) VALUES (?, ?, ?)",
            (college_name, review_text, rating))
        conn.commit()
        conn.close()
        return jsonify({"message": "Review submitted successfully"})
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
