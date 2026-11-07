
import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold
)

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# 1. File paths
BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "intent_data.csv"
MODEL_PATH = BASE_DIR / "best_intent_model_candidate.pkl"


# 2. Load dataset
data = pd.read_csv(DATA_PATH)
data = data.dropna(subset=["text", "intent"])

data["text"] = data["text"].astype(str).str.strip()
data = data[data["text"] != ""]

X = data["text"]
y = data["intent"]

print("Dataset loaded:", len(data), "examples")


# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training examples:", len(X_train))
print("Testing examples:", len(X_test))


# 4. Define word TF-IDF
word_vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    sublinear_tf=True
)


# 5. Define combined word + character TF-IDF
combined_vectorizer = FeatureUnion([
    (
        "word",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
    ),
    (
        "character",
        TfidfVectorizer(
            lowercase=True,
            analyzer="char_wb",
            ngram_range=(2, 5),
            sublinear_tf=True
        )
    )
])


# 6. Define experiments
experiments = {

    "D1 - Word + Logistic Regression": {
        "vectorizer": word_vectorizer,
        "classifier": LogisticRegression(
            C=10,
            max_iter=1000,
            random_state=42
        ),
        "parameters": {
            "classifier__C": [1, 10, 100]
        }
    },

    "D2 - Word + Linear SVM": {
        "vectorizer": word_vectorizer,
        "classifier": LinearSVC(
            C=1,
            random_state=42,
            max_iter=5000
        ),
        "parameters": {
            "classifier__C": [0.1, 1, 10]
        }
    },

    "D3 - Combined + Logistic Regression": {
        "vectorizer": combined_vectorizer,
        "classifier": LogisticRegression(
            C=1,
            max_iter=1000,
            random_state=42
        ),
        "parameters": {
            "classifier__C": [0.1, 1, 10]
        }
    },

    "D4 - Combined + Linear SVM": {
        "vectorizer": combined_vectorizer,
        "classifier": LinearSVC(
            C=1,
            random_state=42,
            max_iter=5000
        ),
        "parameters": {
            "classifier__C": [0.1, 1, 10]
        }
    }
}


# 7. Cross-validation setup
cross_validation = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# 8. Train and evaluate experiments
results = []
trained_models = {}

for name, experiment in experiments.items():

    print("\n================================")
    print("Running:", name)
    print("================================")

    pipeline = Pipeline([
        ("tfidf", experiment["vectorizer"]),
        ("classifier", experiment["classifier"])
    ])

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=experiment["parameters"],
        scoring="f1_macro",
        cv=cross_validation,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_

    predictions = best_model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    results.append({
        "Experiment": name,
        "Best Parameters": str(grid_search.best_params_),
        "CV Macro F1": round(grid_search.best_score_, 4),
        "Test Accuracy": round(accuracy * 100, 2),
        "Test Macro F1": round(macro_f1, 4)
    })

    trained_models[name] = best_model

    print("\nBest parameters:", grid_search.best_params_)
    print("CV Macro F1:", round(grid_search.best_score_, 4))
    print("Test Accuracy:", round(accuracy * 100, 2), "%")
    print("Test Macro F1:", round(macro_f1, 4))

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))


# 9. Compare experiments
results_df = pd.DataFrame(results)

print("\n========== FINAL COMPARISON ==========")
print(results_df.to_string(index=False))


# 10. Select best model using CV Macro F1
best_index = results_df["CV Macro F1"].idxmax()

best_name = results_df.loc[best_index, "Experiment"]
best_model = trained_models[best_name]

print("\nBest configuration:", best_name)

best_predictions = best_model.predict(X_test)

print("\nBest model confusion matrix:")
print(confusion_matrix(
    y_test,
    best_predictions,
    labels=best_model.classes_
))


# 11. Save shortlisted candidate models

# Candidate 1: Word TF-IDF + Linear SVM
word_svm = trained_models["D2 - Word + Linear SVM"]

joblib.dump(
    word_svm,
    BASE_DIR / "word_svm_candidate.pkl"
)

# Candidate 2: Combined TF-IDF + Linear SVM
combined_svm = trained_models["D4 - Combined + Linear SVM"]

joblib.dump(
    combined_svm,
    BASE_DIR / "best_intent_model_candidate.pkl"
)

# Save experiment results
results_df.to_csv(
    BASE_DIR / "feature_classifier_comparison.csv",
    index=False
)

print("\nBoth shortlisted models saved successfully!")
