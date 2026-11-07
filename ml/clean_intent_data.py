import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "intent_data.csv"

df = pd.read_csv(DATA_PATH)

df = df.drop_duplicates(
    subset=["text", "intent"],
    keep="first"
)

df.to_csv(DATA_PATH, index=False)

print("Cleaned dataset:", len(df))
print("\nUpdated intent distribution:")
print(df["intent"].value_counts().sort_index())