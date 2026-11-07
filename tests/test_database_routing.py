import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chatbot import search_books, extract_search_query

tests = [
    ("Show me books by Rick Riordan", "author_search"),
    ("Show me your fantasy collection", "genre_search"),
    ("Do you have Atomic Habits?", "book_search")
]

for message, intent in tests:

    query = extract_search_query(message, intent)

    if intent == "author_search":
        results = search_books(query, "author")
    elif intent == "genre_search":
        results = search_books(query, "genre")
    else:
        results = search_books(query)

    print(f"\n{message}")
    print(f"Query: {query}")
    print(f"Database matches: {len(results)}")

    for book in results:
        print("-", book[1], "|", book[2])