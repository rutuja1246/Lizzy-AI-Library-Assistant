import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# 1. File paths
BASE_DIR = Path(__file__).resolve().parent

TRAIN_PATH = BASE_DIR / "intent_data.csv"
EVAL_PATH = BASE_DIR / "intent_eval.csv"

MODELS = {
    "Word + Linear SVM": BASE_DIR / "word_svm_candidate.pkl",
    "Combined + Linear SVM": BASE_DIR / "best_intent_model_candidate.pkl"
}

# 2. Load datasets
train_df = pd.read_csv(TRAIN_PATH)
eval_df = pd.read_csv(EVAL_PATH)

X_eval = eval_df["text"]
y_eval = eval_df["intent"]

# 3. Check exact sentence overlap
train_texts = set(
    train_df["text"].str.strip().str.lower()
)

eval_texts = set(
    eval_df["text"].str.strip().str.lower()
)

overlap = train_texts.intersection(eval_texts)

print("Evaluation examples:", len(eval_df))
print("Exact training/evaluation overlaps:", len(overlap))

if overlap:
    print("\nOverlapping sentences:")
    for sentence in sorted(overlap):
        print("-", sentence)

    raise ValueError(
        "Evaluation data contains training examples."
    )

# 4. Evaluate saved models
results = []

for model_name, model_path in MODELS.items():

    print("\n" + "=" * 50)
    print("Evaluating:", model_name)
    print("=" * 50)

    model = joblib.load(model_path)

    predictions = model.predict(X_eval)

    accuracy = accuracy_score(y_eval, predictions)

    macro_f1 = f1_score(
        y_eval,
        predictions,
        average="macro",
        zero_division=0
    )

    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Macro F1:", round(macro_f1, 4))

    print("\nClassification Report:")
    print(classification_report(
        y_eval,
        predictions,
        zero_division=0
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(
        y_eval,
        predictions,
        labels=model.classes_
    ))

    results.append({
        "Model": model_name,
        "Accuracy": round(accuracy * 100, 2),
        "Macro F1": round(macro_f1, 4)
    })

# 5. Final comparison
results_df = pd.DataFrame(results)

print("\n========== FRESH EVALUATION COMPARISON ==========")
print(results_df.to_string(index=False))

print("\nEvaluation completed!")