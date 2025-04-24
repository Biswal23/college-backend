import sqlite3

# Connect to the SQLite database (college.db)
def get_db_connection():
    conn = sqlite3.connect('college.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Define the db object
db = get_db_connection()