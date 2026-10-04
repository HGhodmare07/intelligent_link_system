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


TEST_FILE = ROOT / "data" / "processed" / "test.csv"
MODEL_FILE = ROOT / "model" / "url_model_v2.joblib"

# IMPORTANT:
# Selected using validation data only.
THRESHOLD = 0.30


print("=" * 70)
print("FINAL V2 TEST EVALUATION")
print("=" * 70)

# ------------------------------------------------------------
# LOAD TEST DATA
# ------------------------------------------------------------

df = pd.read_csv(
    TEST_FILE,
    usecols=["url_clean", "label"]
)

print()
print("Test rows:", len(df))

# ------------------------------------------------------------
# BUILD FEATURES
# ------------------------------------------------------------

print()
print("Building V2 features...")

rows = []

for url in df["url_clean"]:
    clean = normalize_url(url)
    rows.append(extract_features(clean))

X_test = pd.DataFrame(
    rows,
    columns=FEATURE_NAMES
)

y_test = (df["label"] != 0).astype(int)

print("Features:", X_test.shape[1])

# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

model = joblib.load(MODEL_FILE)

print()
print("Model loaded:")
print(MODEL_FILE)

# ------------------------------------------------------------
# PREDICT
# ------------------------------------------------------------

probs = model.predict_proba(X_test)

p_malicious = 1 - probs[:, 0]

y_pred = (
    p_malicious >= THRESHOLD
).astype(int)

# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0,
)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    y_pred,
).ravel()

false_positive_rate = (
    fp / (fp + tn)
)

false_negative_rate = (
    fn / (fn + tp)
)

# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

print()
print("=" * 70)
print("FINAL V2 RESULTS")
print("=" * 70)

print(
    f"Threshold:            {THRESHOLD:.2f}"
)

print(
    f"Precision:            {precision:.4f}"
)

print(
    f"Recall:               {recall:.4f}"
)

print(
    f"F1:                   {f1:.4f}"
)

print(
    f"False Positive Rate:  {false_positive_rate:.4f}"
)

print(
    f"False Negative Rate:  {false_negative_rate:.4f}"
)

print()
print("Confusion Matrix:")
print()

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)

print()
print("TN:", tn)
print("FP:", fp)
print("FN:", fn)
print("TP:", tp)

print()
print("=" * 70)
print("FINAL V2 TEST EVALUATION COMPLETE")
print("=" * 70)