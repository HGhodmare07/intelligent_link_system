import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEST_FILE = ROOT / "data" / "processed" / "test.csv"

print("=" * 70)
print("V2 FEATURE ERROR COMPARISON")
print("=" * 70)

# ------------------------------------------------------------
# LOAD TEST DATA
# ------------------------------------------------------------

df = pd.read_csv(
    TEST_FILE,
    usecols=["url_clean", "label"]
)

# ------------------------------------------------------------
# LOAD V2 FEATURES
# ------------------------------------------------------------

import sys

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)

rows = []

for url in df["url_clean"]:
    clean = normalize_url(url)
    rows.append(extract_features(clean))

X = pd.DataFrame(
    rows,
    columns=FEATURE_NAMES
)

data = pd.concat(
    [
        X,
        df.reset_index(drop=True)
    ],
    axis=1
)

# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

import joblib

MODEL_FILE = ROOT / "model" / "url_model_v2.joblib"

model = joblib.load(MODEL_FILE)

probs = model.predict_proba(X)

p_malicious = 1 - probs[:, 0]

pred = (
    p_malicious >= 0.30
).astype(int)

data["p_malicious"] = p_malicious
data["predicted"] = pred

# ------------------------------------------------------------
# GROUPS
# ------------------------------------------------------------

# Actual malicious URLs correctly detected
TP = data[
    (data["label"] != 0) &
    (data["predicted"] == 1)
]

# Actual malicious URLs missed
FN = data[
    (data["label"] != 0) &
    (data["predicted"] == 0)
]

# Benign URLs correctly allowed
TN = data[
    (data["label"] == 0) &
    (data["predicted"] == 0)
]

# Benign URLs incorrectly blocked
FP = data[
    (data["label"] == 0) &
    (data["predicted"] == 1)
]

print()
print("TP:", len(TP))
print("FN:", len(FN))
print("TN:", len(TN))
print("FP:", len(FP))

# ------------------------------------------------------------
# FEATURE MEAN COMPARISON
# ------------------------------------------------------------

print()
print("=" * 70)
print("MALICIOUS: TRUE POSITIVE vs FALSE NEGATIVE")
print("=" * 70)

comparison = pd.DataFrame({
    "TP_mean": TP[FEATURE_NAMES].mean(),
    "FN_mean": FN[FEATURE_NAMES].mean(),
})

comparison["absolute_difference"] = (
    comparison["TP_mean"] -
    comparison["FN_mean"]
).abs()

print(
    comparison
    .sort_values(
        "absolute_difference",
        ascending=False
    )
    .head(20)
    .round(4)
    .to_string()
)

# ------------------------------------------------------------
# BENIGN: TRUE NEGATIVE vs FALSE POSITIVE
# ------------------------------------------------------------

print()
print("=" * 70)
print("BENIGN: TRUE NEGATIVE vs FALSE POSITIVE")
print("=" * 70)

comparison2 = pd.DataFrame({
    "TN_mean": TN[FEATURE_NAMES].mean(),
    "FP_mean": FP[FEATURE_NAMES].mean(),
})

comparison2["absolute_difference"] = (
    comparison2["TN_mean"] -
    comparison2["FP_mean"]
).abs()

print(
    comparison2
    .sort_values(
        "absolute_difference",
        ascending=False
    )
    .head(20)
    .round(4)
    .to_string()
)

# ------------------------------------------------------------
# PHISHING SPECIFIC
# ------------------------------------------------------------

print()
print("=" * 70)
print("PHISHING: TRUE POSITIVE vs FALSE NEGATIVE")
print("=" * 70)

PHISH_TP = data[
    (data["label"] == 2) &
    (data["predicted"] == 1)
]

PHISH_FN = data[
    (data["label"] == 2) &
    (data["predicted"] == 0)
]

print()
print("Phishing TP:", len(PHISH_TP))
print("Phishing FN:", len(PHISH_FN))

phish_comparison = pd.DataFrame({
    "TP_mean": PHISH_TP[FEATURE_NAMES].mean(),
    "FN_mean": PHISH_FN[FEATURE_NAMES].mean(),
})

phish_comparison["absolute_difference"] = (
    phish_comparison["TP_mean"] -
    phish_comparison["FN_mean"]
).abs()

print(
    phish_comparison
    .sort_values(
        "absolute_difference",
        ascending=False
    )
    .head(20)
    .round(4)
    .to_string()
)

print()
print("=" * 70)
print("FEATURE COMPARISON COMPLETE")
print("=" * 70)