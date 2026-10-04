
from pathlib import Path
import sys

import joblib
import pandas as pd


# --------------------------------------------------
# PATHS AND IMPORTS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES
)


MODEL_FILE = ROOT / "model" / "url_model_binary.joblib"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"

LOW_THRESHOLD = 0.20
HIGH_THRESHOLD = 0.90


print("=" * 70)
print("V2 THREE-WAY SECURITY TEST EVALUATION")
print("=" * 70)


# --------------------------------------------------
# LOAD AND VERIFY MODEL
# --------------------------------------------------

if not MODEL_FILE.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

if not TEST_FILE.exists():
    raise FileNotFoundError(f"Test dataset not found: {TEST_FILE}")

model = joblib.load(MODEL_FILE)

# Verify binary classification
assert list(model.classes_) == [0, 1], (
    f"Expected binary classes [0, 1], got {model.classes_}"
)

# Verify feature count
assert model.n_features_in_ == len(FEATURE_NAMES), (
    f"Model expects {model.n_features_in_} features, "
    f"but FEATURE_NAMES contains {len(FEATURE_NAMES)}"
)

print("\nModel loaded:", MODEL_FILE.name)
print("Model classes:", model.classes_)
print("Model feature count:", model.n_features_in_)


# --------------------------------------------------
# LOAD UNTOUCHED TEST SET
# --------------------------------------------------

df = pd.read_csv(
    TEST_FILE,
    usecols=["url_clean", "label"]
)

df = df.dropna(subset=["url_clean", "label"]).copy()
df["label"] = df["label"].astype(int)

print("\nTest rows:", len(df))


# --------------------------------------------------
# BUILD FEATURES
# --------------------------------------------------

print("\nBuilding test features...")

X = pd.DataFrame(
    [
        extract_features(normalize_url(url))
        for url in df["url_clean"]
    ],
    columns=FEATURE_NAMES
)

# Verify feature order and count
assert list(X.columns) == list(FEATURE_NAMES), (
    "Feature order mismatch"
)

assert X.shape[1] == model.n_features_in_, (
    "Input feature count does not match model"
)

print("Feature matrix shape:", X.shape)


# --------------------------------------------------
# PREDICT PROBABILITIES
# --------------------------------------------------

print("\nPredicting probabilities...")

probabilities = model.predict_proba(X)

classes = list(model.classes_)

benign_index = classes.index(0)
malicious_index = classes.index(1)

p_malicious = probabilities[:, malicious_index]


# --------------------------------------------------
# THREE-WAY DECISION
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
    df["label"] > 0
).map({
    False: "BENIGN",
    True: "MALICIOUS"
})


# --------------------------------------------------
# DECISION DISTRIBUTION
# --------------------------------------------------

print("\n" + "=" * 70)
print("DECISION DISTRIBUTION")
print("=" * 70)

distribution = pd.crosstab(
    df["binary_label"],
    df["decision"]
).reindex(
    index=["BENIGN", "MALICIOUS"],
    columns=["ALLOW", "REVIEW", "BLOCK"],
    fill_value=0
)

print(distribution.to_string())


# --------------------------------------------------
# DECISION PERCENTAGES
# --------------------------------------------------

print("\n" + "=" * 70)
print("DECISION PERCENTAGES")
print("=" * 70)

percentage_table = pd.crosstab(
    df["binary_label"],
    df["decision"],
    normalize="index"
).reindex(
    index=["BENIGN", "MALICIOUS"],
    columns=["ALLOW", "REVIEW", "BLOCK"],
    fill_value=0
) * 100

print(percentage_table.round(2).to_string())


# --------------------------------------------------
# MALICIOUS CLASS BREAKDOWN
# --------------------------------------------------

print("\n" + "=" * 70)
print("MALICIOUS CLASS BREAKDOWN")
print("=" * 70)

malicious = df[df["label"] > 0].copy()

print(
    pd.crosstab(
        malicious["label"],
        malicious["decision"]
    ).to_string()
)


# --------------------------------------------------
# BENIGN URL BREAKDOWN
# --------------------------------------------------

print("\n" + "=" * 70)
print("BENIGN URLs")
print("=" * 70)

benign = df[df["label"] == 0]

print(
    benign["decision"]
    .value_counts()
    .reindex(["ALLOW", "REVIEW", "BLOCK"], fill_value=0)
    .to_string()
)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("LOW threshold :", LOW_THRESHOLD)
print("HIGH threshold:", HIGH_THRESHOLD)

print()

total = len(df)

for decision in ["ALLOW", "REVIEW", "BLOCK"]:
    count = (df["decision"] == decision).sum()
    percentage = (count / total * 100) if total else 0

    print(
        f"{decision:6} = {count} ({percentage:.2f}%)"
    )


# --------------------------------------------------
# SECURITY INTERPRETATION
# --------------------------------------------------

print("\n" + "=" * 70)
print("SECURITY INTERPRETATION")
print("=" * 70)

malicious_total = len(malicious)
benign_total = len(benign)

malicious_allowed = (
    (malicious["decision"] == "ALLOW").sum()
)

malicious_reviewed = (
    (malicious["decision"] == "REVIEW").sum()
)

malicious_blocked = (
    (malicious["decision"] == "BLOCK").sum()
)

benign_allowed = (
    (benign["decision"] == "ALLOW").sum()
)

benign_reviewed = (
    (benign["decision"] == "REVIEW").sum()
)

benign_blocked = (
    (benign["decision"] == "BLOCK").sum()
)

print(
    f"Malicious URLs ALLOWED: "
    f"{malicious_allowed} / {malicious_total}"
)

print(
    f"Malicious URLs sent to REVIEW: "
    f"{malicious_reviewed} / {malicious_total}"
)

print(
    f"Malicious URLs BLOCKED: "
    f"{malicious_blocked} / {malicious_total}"
)

print(
    f"Benign URLs ALLOWED: "
    f"{benign_allowed} / {benign_total}"
)

print(
    f"Benign URLs sent to REVIEW: "
    f"{benign_reviewed} / {benign_total}"
)

print(
    f"Benign URLs incorrectly BLOCKED: "
    f"{benign_blocked} / {benign_total}"
)

print("\nTest evaluation completed.")