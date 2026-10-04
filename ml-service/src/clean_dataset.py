import os
import pandas as pd
from features import normalize_url   # same normalizer the API will use later

RAW_PATH = "data/raw/malicious_urls.csv"
OUT_PATH = "data/processed/clean_urls.csv"

# We only need the raw URL and the label. Every feature will be
# computed from the URL string by our own code in features.py.
df = pd.read_csv(RAW_PATH, usecols=["url", "label"], low_memory=False)
print("Rows loaded:", len(df))

# 1. Drop rows with a missing URL or label.
df = df.dropna(subset=["url", "label"])

# 2. Normalize every URL (this removes the formatting shortcut).
df["url_clean"] = df["url"].apply(normalize_url)

# 3. Drop rows whose URL became empty after normalizing.
df = df[df["url_clean"] != ""]
after_basic = len(df)

# 4. Find URLs that appear with MORE THAN ONE different label (conflicts).
#    nunique() counts distinct labels per URL; more than 1 = contradiction.
labels_per_url = df.groupby("url_clean")["label"].nunique()
conflict_urls = labels_per_url[labels_per_url > 1].index
print("URLs with conflicting labels (removed entirely):", len(conflict_urls))
df = df[~df["url_clean"].isin(conflict_urls)]   # ~ means "not in"

# 5. Remove duplicates: keep one row per URL.
before_dedup = len(df)
df = df.drop_duplicates(subset="url_clean", keep="first")
print("Duplicate rows removed:", before_dedup - len(df))

# 6. Save only what training needs.
df = df[["url_clean", "label"]].reset_index(drop=True)
os.makedirs("data/processed", exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("\nRows after basic cleaning:", after_basic)
print("Final rows saved         :", len(df))
print("\nClass counts:")
print(df["label"].value_counts().sort_index().to_string())
print("\nSaved to:", OUT_PATH)
print("\nSample:")
print(df.sample(5, random_state=1).to_string(index=False))