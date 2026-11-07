
import re
import joblib

from pathlib import Path
from database import get_connection

# -----------------------------
# 1. Load trained intent model
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR / "ml" / "best_intent_model_candidate.pkl"
)

intent_model = joblib.load(MODEL_PATH)

print("Lizzy intent model loaded successfully!")

# -----------------------------
# 2. Predict user intent
# -----------------------------

def predict_intent(message):

    scores = intent_model.decision_function([message])[0]

    ranked_scores = sorted(
        zip(intent_model.classes_, scores),
        key=lambda item: item[1],
        reverse=True
    )

    predicted_intent = ranked_scores[0][0]
    highest_score = ranked_scores[0][1]
    second_highest_score = ranked_scores[1][1]

    score_margin = highest_score - second_highest_score

    return {
        "intent": predicted_intent,
        "highest_score": float(highest_score),
        "second_highest_score": float(second_highest_score),
        "score_margin": float(score_margin)
    }

# -----------------------------
# Extract search terms
# -----------------------------

def extract_search_query(message, intent):

    text = message.lower().strip()
    text = text.rstrip("?!., ")

    # -----------------------------
    # Author search
    # -----------------------------
    if intent == "author_search":

        patterns = [
            r"books by (.+)",
            r"book by (.+)",
            r"works by (.+)",
            r"books written by (.+)",
            r"written by (.+)",
            r"authored by (.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return match.group(1).strip(" ?.!,")

    # -----------------------------
    # Genre search
    # -----------------------------
    if intent == "genre_search":

        patterns = [
            r"(?:show me|find|search for|list|browse)\s+(?:your\s+)?(.+?)\s+books",
            r"(?:show me|browse)\s+(?:your\s+)?(.+?)\s+collection",
            r"books in (?:the )?(.+?) genre",
            r"books about (.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return match.group(1).strip(" ?.!,")

    # -----------------------------
    # Book, availability and shelf queries
    # -----------------------------

    prefixes = [
        "where can i find ",
        "where is ",
        "where have you placed ",
        "which shelf contains ",
        "tell me the shelf code for ",
        "what shelf is ",
        "do you have ",
        "can i find ",
        "can i borrow ",
        "is ",
        "find ",
        "show me ",
        "search for ",
        "look up ",
        "locate ",
        "tell me about "
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    # Remove common question endings
    suffixes = [
        " currently available",
        " available",
        " in stock",
        " right now",
        " please",
        " book"
    ]

    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[:-len(suffix)]

    return text.strip(" ?!.,")

# -----------------------------
# 1. Search the library database
# -----------------------------

def search_books(query, search_field="all"):
    conn = get_connection()
    cursor = conn.cursor()

    search_term = f"%{query.strip()}%"

    if search_field == "genre":
        cursor.execute("""
            SELECT id, title, author, genre, shelf, available, copies
            FROM books
            WHERE genre LIKE ?
            ORDER BY title
        """, (search_term,))

    elif search_field == "author":
        cursor.execute("""
            SELECT id, title, author, genre, shelf, available, copies
            FROM books
            WHERE author LIKE ?
            ORDER BY title
        """, (search_term,))

    else:
        cursor.execute("""
            SELECT id, title, author, genre, shelf, available, copies
            FROM books
            WHERE title LIKE ?
               OR author LIKE ?
               OR genre LIKE ?
            ORDER BY title
        """, (search_term, search_term, search_term))

    results = cursor.fetchall()
    conn.close()

    return results


# -----------------------------
# 2. Format book information
# -----------------------------

def format_book(book):
    _, title, author, genre, shelf, available, copies = book

    if copies > 0:
        availability = (
            f"Yes! {copies} "
            f"{'copy' if copies == 1 else 'copies'} available."
        )
    else:
        availability = "Sorry, this book is currently unavailable."

    return (
        f"📖 {title}\n"
        f"Author: {author}\n"
        f"Genre: {genre}\n"
        f"Shelf: {shelf}\n"
        f"{availability}"
    )


def format_book_list(books):
    response = f"I found {len(books)} book(s) in our catalogue:\n\n"

    for book in books:
        _, title, author, genre, shelf, available, copies = book

        response += (
            f"📖 {title}\n"
            f"Author: {author}\n"
            f"Shelf: {shelf}\n"
            f"Available copies: {copies}\n\n"
        )

    return response.strip()


def format_availability(book):

    title = book[1]
    copies = book[6]

    if copies > 0:
        return (
            f"Yes! {title} is available. "
            f"We currently have {copies} "
            f"{'copy' if copies == 1 else 'copies'}."
        )

    return f"Sorry, {title} is currently unavailable."


def format_shelf_location(book):

    title = book[1]
    shelf = book[4]

    return (
        f"📖 {title} is located on shelf {shelf}."
    )


# -----------------------------
# 3. Understand the user's intent
# -----------------------------

def get_intent(message):
    text = message.lower().strip()
    text = re.sub(r"[?!.,]", "", text)
    text = re.sub(r"\s+", " ", text)

    # Greetings
    greetings = [
        "hi", "hello", "hey", "hii", "hiii",
        "good morning", "good afternoon", "good evening"
    ]

    if text in greetings:
        return "greeting", ""

    # Help
    if text in ["help", "what can you do", "how can you help"]:
        return "help", ""

    # Search by author
    author_patterns = [
        r"books by (.+)",
        r"book by (.+)",
        r"works by (.+)",
        r"books written by (.+)",
        r"find books by (.+)"
    ]

    for pattern in author_patterns:
        match = re.search(pattern, text)

        if match:
            return "author", match.group(1).strip()

    # Search by genre
    genre_patterns = [
        r"(?:find|show me|search for|list|i want) (.+?) books",
        r"books in (?:the )?(.+?) genre",
        r"books about (.+)"
    ]

    for pattern in genre_patterns:
        match = re.search(pattern, text)

        if match:
            return "genre", match.group(1).strip()

    # Remove common question phrases
    prefixes = [
        "where can i find ",
        "where is ",
        "do you have ",
        "can i find ",
        "find ",
        "search for ",
        "show me ",
        "tell me about ",
        "is ",
        "have you got "
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    # Remove words that are not part of the book title
    suffixes = [
        " available",
        " in stock",
        " currently available",
        " please",
        " book"
    ]

    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[:-len(suffix)]

    text = text.strip()

    # Remove a trailing plural "books" for genre searches
    if text.endswith(" books"):
        text = text[:-6].strip()
        return "genre", text

    return "book", text


# -----------------------------
# 4. Generate the chatbot response
# -----------------------------

def get_response(message):

    if not message or not message.strip():
        return "Please enter a message so I can help you!"

    result = predict_intent(message)
    intent = result["intent"]

    # Greeting
    if intent == "greeting":
        return (
            "Hello! I'm Lizzy, your smart library companion. 📚\n"
            "I can help you find books, check availability, "
            "and locate their shelves. What are you looking for?"
        )

    # Help
    if intent == "help":
        return (
            "Here's what I can help you with! 📚\n\n"
            "• Search for books by title\n"
            "• Find books by an author\n"
            "• Browse books by genre\n"
            "• Check book availability\n"
            "• Find a book's shelf location\n"
            "• Get reading recommendations\n"
            "• Ask library-related questions"
        )

    # Unknown
    if intent == "unknown":
        return (
            "I'm sorry, I can currently help with library-related "
            "questions. Try asking me to find a book or check its availability!"
        )

    # Recommendation
    if intent == "recommendation":
        return (
            "I'd love to help you discover your next read! 📚 "
            "Our personalised recommendation feature is still being developed. "
            "Try browsing our available books by genre for now."
        )

    # FAQ
    if intent == "library_faq":
        return (
            "I don't have an answer for that question in my FAQ collection yet. "
            "Please check with the library staff."
        )

    # Extract query for database-related intents
    query = extract_search_query(message, intent)

    if not query:
        return "Could you tell me which book, author or genre you're looking for?"

    # Author search
    if intent == "author_search":
        books = search_books(query, "author")

        if not books:
            return f"I couldn't find any books by {query} in our catalogue."

        return format_book_list(books)

    # Genre search
    if intent == "genre_search":
        books = search_books(query, "genre")

        if not books:
            return f"I couldn't find any books in the {query} genre."

        return format_book_list(books)

    # Book search
    if intent == "book_search":
        books = search_books(query)

        if not books:
            return (
                "I couldn't find that book in our catalogue. "
                "Would you like to try another title or author?"
            )

        if len(books) > 1:
            return format_book_list(books)

        return format_book(books[0])

    # Availability check
    if intent == "availability_check":
        books = search_books(query)

        if not books:
            return f"I couldn't find {query} in our catalogue."

        if len(books) > 1:
            return format_book_list(books)

        return format_availability(books[0])

    # Shelf lookup
    if intent == "shelf_lookup":
        books = search_books(query)

        if not books:
            return f"I couldn't find {query} in our catalogue."

        if len(books) > 1:
            return format_book_list(books)

        return format_shelf_location(books[0])

    return "I'm not sure how to help with that request."