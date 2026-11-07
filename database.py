
import sqlite3
from pathlib import Path

# ============================
# DATABASE CONFIGURATION
# ============================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "books.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


# ============================
# SAMPLE BOOK DATA
# ============================

books = [

    ("Atomic Habits", "James Clear", "Self Help", "A1", 1, 3),
    ("Deep Work", "Cal Newport", "Productivity", "A2", 1, 2),
    ("Python Crash Course", "Eric Matthes", "Programming", "B1", 1, 4),
    ("Clean Code", "Robert C. Martin", "Programming", "B2", 0, 0),
    ("Fluent Python", "Luciano Ramalho", "Programming", "B3", 1, 2),
    ("The Pragmatic Programmer", "Andrew Hunt", "Programming", "B4", 1, 1),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Programming", "B5", 1, 2),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "AI", "C1", 1, 2),
    ("Hands-On Machine Learning", "Aurélien Géron", "AI", "C2", 1, 3),
    ("Deep Learning with Python", "François Chollet", "AI", "C3", 0, 0),
    ("Dune", "Frank Herbert", "Science Fiction", "D1", 1, 2),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "D2", 1, 5),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy", "D3", 1, 6),
    ("Percy Jackson and the Lightning Thief", "Rick Riordan", "Fantasy", "D4", 1, 4),
    ("The Heroes of Olympus", "Rick Riordan", "Fantasy", "D5", 1, 2),
    ("Magnus Chase and the Sword of Summer", "Rick Riordan", "Fantasy", "D6", 1, 2),
    ("The Psychology of Money", "Morgan Housel", "Finance", "E1", 1, 3),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance", "E2", 0, 0),
    ("Sapiens", "Yuval Noah Harari", "History", "F1", 1, 2),
    ("Ikigai", "Héctor García", "Self Help", "F2", 1, 3)

]


# ============================
# INITIALIZE DATABASE
# ============================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            shelf TEXT,
            available INTEGER,
            copies INTEGER
        )
    """)

    # FAQs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        )
    """)

    # Chat logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT,
            timestamp TEXT
        )
    """)

    # Insert sample books only if catalogue is empty
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO books
            (title, author, genre, shelf, available, copies)
            VALUES (?, ?, ?, ?, ?, ?)
        """, books)

        print(f"Inserted {len(books)} sample books.")

    else:
        print(f"Catalogue already contains {count} books. Skipping insertion.")

    conn.commit()
    conn.close()

    print(f"Database initialized: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()
