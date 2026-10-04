import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)


VAL_FILE = ROOT / "data" / "processed" / "val.csv"
MODEL_FILE = ROOT / "model" / "url_model_v2.joblib"


print("=" * 70)
print("V2 VALIDATION THRESHOLD SELECTION")
print("=" * 70)

# ------------------------------------------------------------
# LOAD VALIDATION DATA
# ------------------------------------------------------------

df = pd.read_csv(
    VAL_FILE,
    usecols=["url_clean", "label"]
)

print()
print("Validation rows:", len(df))

# ------------------------------------------------------------
# BUILD FEATURES
# ------------------------------------------------------------

print()
print("Building V2 features...")

rows = []

for url in df["url_clean"]:
    clean = normalize_url(url)
    rows.append(extract_features(clean))

X_val = pd.DataFrame(
    rows,
    columns=FEATURE_NAMES
)

# Convert multiclass labels into:
# 0 = benign
# 1 = malicious
y_val = (df["label"] != 0).astype(int)

print("Features:", X_val.shape[1])

# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

model = joblib.load(MODEL_FILE)

print()
print("Model loaded:")
print(MODEL_FILE)

# ------------------------------------------------------------
# GET MALICIOUS PROBABILITY
# ------------------------------------------------------------

probs = model.predict_proba(X_val)

p_malicious = 1 - probs[:, 0]

# ------------------------------------------------------------
# TEST THRESHOLDS ON VALIDATION SET
# ------------------------------------------------------------

thresholds = [
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
]

results = []

for threshold in thresholds:

    y_pred = (
        p_malicious >= threshold
    ).astype(int)

    precision = precision_score(
        y_val,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_val,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_val,
        y_pred,
        zero_division=0,
    )

    tn, fp, fn, tp = confusion_matrix(
        y_val,
        y_pred,
    ).ravel()

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    false_negative_rate = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0
    )

    results.append({
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
    })


result_df = pd.DataFrame(results)

# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

print()
print("=" * 70)
print("V2 VALIDATION THRESHOLD RESULTS")
print("=" * 70)

print(
    result_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)

# ------------------------------------------------------------
# BEST THRESHOLD
# ------------------------------------------------------------

best = result_df.loc[
    result_df["f1"].idxmax()
]

print()
print("=" * 70)
print("SELECTED V2 THRESHOLD")
print("=" * 70)

print(
    f"Threshold: {best['threshold']:.2f}"
)

print(
    f"Precision: {best['precision']:.4f}"
)

print(
    f"Recall: {best['recall']:.4f}"
)

print(
    f"F1: {best['f1']:.4f}"
)

print(
    f"False Positive Rate: "
    f"{best['false_positive_rate']:.4f}"
)

print(
    f"False Negative Rate: "
    f"{best['false_negative_rate']:.4f}"
)

print()
print("This threshold will be evaluated on the untouched test set.")