import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import normalize_url, extract_features, FEATURE_NAMES


TEST_FILE = ROOT / "data" / "processed" / "test.csv"
MODEL_FILE = ROOT / "model" / "url_model_v2.joblib"

THRESHOLD = 0.30

print("=" * 70)
print("V2 ERROR ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# LOAD TEST DATA
# ------------------------------------------------------------

df = pd.read_csv(
    TEST_FILE,
    usecols=["url_clean", "label"]
)

print("Test rows:", len(df))

# ------------------------------------------------------------
# BUILD FEATURES
# ------------------------------------------------------------

rows = []

for url in df["url_clean"]:
    clean = normalize_url(url)
    rows.append(extract_features(clean))

X = pd.DataFrame(
    rows,
    columns=FEATURE_NAMES
)

y = (df["label"] != 0).astype(int)

# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

model = joblib.load(MODEL_FILE)

# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

probs = model.predict_proba(X)

p_malicious = 1 - probs[:, 0]

pred = (p_malicious >= THRESHOLD).astype(int)

# ------------------------------------------------------------
# CREATE ERROR DATAFRAME
# ------------------------------------------------------------

result = df.copy()

result["p_malicious"] = p_malicious
result["actual"] = y
result["predicted"] = pred

result["error_type"] = "CORRECT"

result.loc[
    (result["actual"] == 1) & (result["predicted"] == 0),
    "error_type"
] = "FALSE_NEGATIVE"

result.loc[
    (result["actual"] == 0) & (result["predicted"] == 1),
    "error_type"
] = "FALSE_POSITIVE"

# ------------------------------------------------------------
# FALSE NEGATIVES
# ------------------------------------------------------------

fn = result[
    result["error_type"] == "FALSE_NEGATIVE"
].copy()

print()
print("=" * 70)
print("FALSE NEGATIVES")
print("=" * 70)

print("Total:", len(fn))

print()
print("Actual malicious label distribution:")

print(
    fn["label"]
    .value_counts()
    .sort_index()
)

print()
print("Lowest-confidence false negatives:")

print(
    fn[
        [
            "url_clean",
            "label",
            "p_malicious"
        ]
    ]
    .sort_values("p_malicious")
    .head(30)
    .to_string(index=False)
)

# ------------------------------------------------------------
# FALSE POSITIVES
# ------------------------------------------------------------

fp = result[
    result["error_type"] == "FALSE_POSITIVE"
].copy()

print()
print("=" * 70)
print("FALSE POSITIVES")
print("=" * 70)

print("Total:", len(fp))

print()
print("False-positive confidence distribution:")

print(
    fp["p_malicious"]
    .describe()
)

print()
print("Highest-confidence false positives:")

print(
    fp[
        [
            "url_clean",
            "label",
            "p_malicious"
        ]
    ]
    .sort_values(
        "p_malicious",
        ascending=False
    )
    .head(30)
    .to_string(index=False)
)

# ------------------------------------------------------------
# SAVE ERRORS
# ------------------------------------------------------------

OUTPUT_FILE = ROOT / "data" / "processed" / "v2_errors.csv"

result[
    result["error_type"] != "CORRECT"
].to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 70)
print("ERROR ANALYSIS COMPLETE")
print("=" * 70)

print()
print("Saved errors to:")
print(OUTPUT_FILE)