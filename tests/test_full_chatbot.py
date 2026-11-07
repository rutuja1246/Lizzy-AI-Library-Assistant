import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chatbot import get_response

messages = [
    "Hello Lizzy!",
    "Show me books by Rick Riordan",
    "Show me your fantasy collection",
    "Do you have Atomic Habits?",
    "Is Clean Code available?",
    "Where can I find Dune?",
    "Recommend a fantasy book",
    "What can you help me with?",
    "Tell me a joke about computers"
]

for message in messages:

    print("\n" + "=" * 55)
    print("USER:", message)
    print("\nLIZZY:", get_response(message))