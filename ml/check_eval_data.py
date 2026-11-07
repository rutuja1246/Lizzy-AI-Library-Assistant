import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "intent_eval.csv"

df = pd.read_csv(DATA_PATH)

print("Total evaluation examples:", len(df))
print("\nIntent distribution:")
print(df["intent"].value_counts().sort_index())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate examples:")
print(df[df.duplicated(subset=["text"], keep=False)])
