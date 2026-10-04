from pathlib import Path
import sys

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES
)


MODEL_FILE = ROOT / "model" / "url_model_binary.joblib"
VAL_FILE = ROOT / "data" / "processed" / "val.csv"


LOW_THRESHOLD = 0.20
HIGH_THRESHOLD = 0.90


print("=" * 70)
print("V2 THREE-WAY SECURITY EVALUATION")
print("=" * 70)

model = joblib.load(MODEL_FILE)

df = pd.read_csv(
    VAL_FILE,
    usecols=["url_clean", "label"]
)

print()
print("Validation rows:", len(df))

print()
print("Building features...")

X = pd.DataFrame(
    [
        extract_features(normalize_url(url))
        for url in df["url_clean"]
    ],
    columns=FEATURE_NAMES
)

labels = df["label"].astype(int)

probabilities = model.predict_proba(X)

classes = list(model.classes_)

benign_index = classes.index(0)

p_malicious = (
    1.0 - probabilities[:, benign_index]
)


# --------------------------------------------------
# Three-way decision
# --------------------------------------------------

decisions = []

for probability in p_malicious:

    if probability < LOW_THRESHOLD:
        decisions.append("ALLOW")

    elif probability < HIGH_THRESHOLD:
        decisions.append("REVIEW")

    else:
        decisions.append("BLOCK")


df["decision"] = decisions

df["binary_label"] = (
    labels > 0
).map({
    False: "BENIGN",
    True: "MALICIOUS"
})


print()
print("=" * 70)
print("DECISION DISTRIBUTION")
print("=" * 70)

print(
    pd.crosstab(
        df["binary_label"],
        df["decision"]
    )
)


print()
print("=" * 70)
print("DECISION PERCENTAGES")
print("=" * 70)

table = pd.crosstab(
    df["binary_label"],
    df["decision"],
    normalize="index"
) * 100

print(
    table.round(2).to_string()
)


print()
print("=" * 70)
print("MALICIOUS CLASS BREAKDOWN")
print("=" * 70)

malicious = df[labels > 0].copy()

print(
    pd.crosstab(
        malicious["label"],
        malicious["decision"]
    )
)


print()
print("=" * 70)
print("BENIGN URLs")
print("=" * 70)

benign = df[labels == 0]

print(
    benign["decision"]
    .value_counts()
)


print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print("LOW threshold :", LOW_THRESHOLD)
print("HIGH threshold:", HIGH_THRESHOLD)

print()
print("ALLOW  =", (df["decision"] == "ALLOW").sum())
print("REVIEW =", (df["decision"] == "REVIEW").sum())
print("BLOCK  =", (df["decision"] == "BLOCK").sum())