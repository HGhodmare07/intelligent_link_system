import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v2 import normalize_url, extract_features, FEATURE_NAMES


TEST_FILE = ROOT / "data" / "processed" / "test.csv"
MODEL_FILE = ROOT / "model" / "url_model_v2.joblib"


print("=" * 70)
print("V2 THRESHOLD ANALYSIS")
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
# BUILD V2 FEATURES
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
# PROBABILITIES
# ------------------------------------------------------------

probs = model.predict_proba(X_test)

# Probability of malicious URL
p_malicious = 1 - probs[:, 0]

# ------------------------------------------------------------
# THRESHOLD ANALYSIS
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
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred
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

# ------------------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------------------

result_df = pd.DataFrame(results)

print()
print("=" * 70)
print("V2 THRESHOLD RESULTS")
print("=" * 70)

print(
    result_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# ------------------------------------------------------------
# BEST F1
# ------------------------------------------------------------

best = result_df.loc[
    result_df["f1"].idxmax()
]

print()
print("=" * 70)
print("BEST V2 THRESHOLD BY F1")
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
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)