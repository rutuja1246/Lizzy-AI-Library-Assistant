
import sqlite3
import os

# Check both possible database locations
paths = ["books.db", "data/books.db"]

for db_path in paths:

    if not os.path.exists(db_path):
        continue

    print(f"\n{'='*40}")
    print(f"Database found: {db_path}")
    print(f"{'='*40}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
    """)

    tables = cursor.fetchall()

    print("\nTables:", [table[0] for table in tables])

    # Check book count
    if ("books",) in tables:
        cursor.execute("SELECT COUNT(*) FROM books")
        print("Total books:", cursor.fetchone()[0])

        # Display sample books
        cursor.execute("""
            SELECT title, author, genre, shelf, copies
            FROM books
            LIMIT 5
        """)

        print("\nSample books:")

        for book in cursor.fetchall():
            print(book)

    # Check FAQ count
    if ("faqs",) in tables:
        cursor.execute("SELECT COUNT(*) FROM faqs")
        print("\nTotal FAQs:", cursor.fetchone()[0])

    # Check chat logs
    if ("chat_logs",) in tables:
        cursor.execute("SELECT COUNT(*) FROM chat_logs")
        print("Total chat logs:", cursor.fetchone()[0])

    conn.close()

print("\nDatabase inspection complete!")
