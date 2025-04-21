import sqlite3

# Sample college data (from provided Excel)
college_data = [
    ("ABC Engineering", "Maharashtra", "Mumbai", "UG", 85, 120000),
    ("XYZ Institute", "Karnataka", "Bangalore", "PG", 75, 150000),
    ("Techno College", "Tamil Nadu", "Chennai", "UG", 90, 100000),
    ("Alpha University", "Delhi", "New Delhi", "PG", 80, 180000),
    ("Beta College", "Gujarat", "Ahmedabad", "UG", 70, 90000),
    ("Gamma Institute", "Rajasthan", "Jaipur", "UG", 88, 110000),
    ("Delta Tech", "Punjab", "Ludhiana", "PG", 78, 160000),
    ("Omega University", "Kerala", "Kochi", "UG", 92, 130000),
    ("Sunrise College", "UP", "Lucknow", "UG", 65, 85000),
    ("Future Institute", "MP", "Bhopal", "PG", 82, 140000),
]

# Sample review data
review_data = [
    ("ABC Engineering", "Great faculty and modern labs!", 4.5),
    ("ABC Engineering", "Campus is vibrant but fees are high.", 3.8),
    ("XYZ Institute", "Excellent placement support.", 4.2),
    ("Techno College", "Good infrastructure, average hostel.", 3.5),
    ("Alpha University", "Top-notch research facilities.", 4.8),
]

def init_db():
    # Connect to SQLite database (creates college.db if it doesn't exist)
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    # Create colleges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colleges (
            name TEXT NOT NULL,
            state TEXT NOT NULL,
            location TEXT NOT NULL,
            course_level TEXT NOT NULL,
            cutoff REAL NOT NULL,
            fees REAL NOT NULL
        )
    """)

    # Create reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            college_name TEXT NOT NULL,
            review_text TEXT NOT NULL,
            rating REAL NOT NULL,
            FOREIGN KEY (college_name) REFERENCES colleges(name)
        )
    """)

    # Insert college data
    cursor.executemany("""
        INSERT OR REPLACE INTO colleges (name, state, location, course_level, cutoff, fees)
        VALUES (?, ?, ?, ?, ?, ?)
    """, college_data)

    # Insert review data
    cursor.executemany("""
        INSERT OR REPLACE INTO reviews (college_name, review_text, rating)
        VALUES (?, ?, ?)
    """, review_data)

    # Commit and close
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
