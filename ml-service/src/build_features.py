import pandas as pd
from features import extract_features, FEATURE_NAMES

IN_PATH = "data/processed/clean_urls.csv"
OUT_PATH = "data/processed/features.csv"

df = pd.read_csv(IN_PATH)
print("Rows:", len(df))
print("Number of features:", len(FEATURE_NAMES))

# Run extract_features on every URL. Each call returns a dict, and
# pandas turns a list of dicts into a table (one column per key).
print("Extracting features (1-3 minutes)...")
feats = pd.DataFrame([extract_features(u) for u in df["url_clean"]],
                     columns=FEATURE_NAMES)   # columns= forces our fixed order

# Attach the label and keep the URL so we can inspect rows later.
feats["label"] = df["label"].values
feats["url_clean"] = df["url_clean"].values
feats.to_csv(OUT_PATH, index=False)
print("Saved to:", OUT_PATH)

# ---- Check 1: broken numbers ----
print("\nMissing values in features:", int(feats[FEATURE_NAMES].isnull().sum().sum()))

# ---- Check 2: average of every feature per class ----
print("\n" + "=" * 70)
print("MEAN OF EACH FEATURE BY CLASS (0=benign 1=defacement 2=phishing 3=malware)")
print("=" * 70)
means = feats.groupby("label")[FEATURE_NAMES].mean().T
print(means.round(3).to_string())

# ---- Check 3: the '&amp;' question from Step 4 ----
print("\n" + "=" * 70)
print("SHARE OF EACH CLASS WHOSE URL CONTAINS '&amp;'")
print("=" * 70)
has_amp = feats["url_clean"].str.contains("&amp;", regex=False)
print(has_amp.groupby(feats["label"]).mean().round(4).to_string())