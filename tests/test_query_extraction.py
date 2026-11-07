import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chatbot import extract_search_query

test_cases = [
    ("Show me books by Rick Riordan", "author_search"),
    ("Find books written by J.K. Rowling", "author_search"),
    ("Show me your fantasy collection", "genre_search"),
    ("Find programming books", "genre_search"),
    ("Do you have Atomic Habits?", "book_search"),
    ("Is Clean Code available?", "availability_check"),
    ("Where can I find Dune?", "shelf_lookup")
]

for message, intent in test_cases:

    query = extract_search_query(message, intent)

    print("\nMessage:", message)
    print("Intent:", intent)
    print("Extracted query:", query)