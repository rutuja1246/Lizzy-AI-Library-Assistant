import pandas as pd
from pathlib import Path

# Locate the dataset
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "intent_data.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

print("\n========== DATASET OVERVIEW ==========")
print("Total examples:", len(df))
print("Total intents:", df["intent"].nunique())
print("\nIntent distribution:")
print(df["intent"].value_counts().sort_index())


# 1. Check missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())


# 2. Check exact duplicate rows
print("\n========== EXACT DUPLICATES ==========")
duplicates = df[df.duplicated(keep=False)]

if duplicates.empty:
    print("No exact duplicate rows found.")
else:
    print(duplicates.sort_values("text"))


# 3. Check identical sentences with conflicting labels
print("\n========== CONFLICTING LABELS ==========")

conflicts = (
    df.groupby("text")["intent"]
    .nunique()
)

conflicts = conflicts[conflicts > 1]

if conflicts.empty:
    print("No conflicting labels found.")
else:
    for sentence in conflicts.index:
        print("\nSentence:", sentence)
        print(df[df["text"] == sentence])


# 4. Check duplicate messages regardless of labels
print("\n========== REPEATED SENTENCES ==========")

repeated = df[
    df["text"].str.strip().str.lower().duplicated(keep=False)
]

if repeated.empty:
    print("No repeated sentences found.")
else:
    print(repeated.sort_values("text").to_string(index=False))


print("\n========== AUDIT COMPLETE ==========")