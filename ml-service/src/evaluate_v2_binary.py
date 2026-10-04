import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES
)


MODEL_FILE = ROOT / "model" / "url_model_binary.joblib"
VAL_FILE = ROOT / "data" / "processed" / "val.csv"


print("=" * 70)
print("V2 BINARY SECURITY CALIBRATION")
print("=" * 70)

# Load V2 model
model = joblib.load(MODEL_FILE)

print()
print("Model:", MODEL_FILE)

# Load validation dataset
df = pd.read_csv(
    VAL_FILE,
    usecols=["url_clean", "label"]
)

print("Validation rows:", len(df))

# Build V2 features
print()
print("Building V2 validation features...")

X = pd.DataFrame(
    [
        extract_features(normalize_url(url))
        for url in df["url_clean"]
    ],
    columns=FEATURE_NAMES
)

# Original labels
y_multi = df["label"].astype(int)

# Binary labels
# 0 = benign
# 1 = malicious
y_binary = (y_multi > 0).astype(int)

# Predict probabilities
probabilities = model.predict_proba(X)

classes = list(model.classes_)

benign_index = classes.index(0)

# Probability of malicious
prob_malicious = 1.0 - probabilities[:, benign_index]


thresholds = [
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
]


results = []

for threshold in thresholds:

    prediction = (
        prob_malicious >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_binary,
        prediction,
        labels=[0, 1]
    ).ravel()

    precision = precision_score(
        y_binary,
        prediction,
        zero_division=0
    )

    recall = recall_score(
        y_binary,
        prediction,
        zero_division=0
    )

    f1 = f1_score(
        y_binary,
        prediction,
        zero_division=0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    fnr = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0
    )

    results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "FPR": fpr,
        "FNR": fnr,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
    })


results_df = pd.DataFrame(results)

pd.set_option(
    "display.max_columns",
    None
)


print()
print("=" * 70)
print("BINARY CALIBRATION RESULTS")
print("=" * 70)

print(
    results_df.round(4).to_string(index=False)
)


best_f1 = results_df.loc[
    results_df["F1"].idxmax()
]

print()
print("=" * 70)
print("BEST F1 THRESHOLD")
print("=" * 70)

print(
    best_f1.round(4).to_string()
)


low_fpr = results_df[
    results_df["FPR"] <= 0.05
]

print()
print("=" * 70)
print("THRESHOLDS WITH FPR <= 5%")
print("=" * 70)

if len(low_fpr) == 0:
    print("None")
else:
    print(
        low_fpr.round(4).to_string(index=False)
    )