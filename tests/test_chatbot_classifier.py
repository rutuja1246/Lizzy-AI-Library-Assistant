import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chatbot import predict_intent

messages = [
    "Hello Lizzy!",
    "Recommend a fantasy book",
    "Tell me a joke about computers",
    "Where can I find Dune?"
]

for message in messages:

    result = predict_intent(message)

    print("\nMessage:", message)
    print("Intent:", result["intent"])
    print("Highest score:", round(result["highest_score"], 4))
    print("Second score:", round(result["second_highest_score"], 4))
    print("Score margin:", round(result["score_margin"], 4))