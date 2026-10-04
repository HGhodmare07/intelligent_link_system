
import os
import sys
import joblib
import pandas as pd

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(
    0,
    os.path.join(PROJECT_ROOT, "src")
)

from features_v3 import extract_features, FEATURE_NAMES


VAL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "val.csv"
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "model",
    "url_model_v3.joblib"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

THRESHOLDS = [
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


# ---------------------------------------------------------
# Load validation data
# ---------------------------------------------------------

print("=" * 70)
print("V3 THRESHOLD SELECTION")
print("=" * 70)

print()
print("Loading validation dataset...")

df = pd.read_csv(VAL_PATH)

print(
    "Validation rows:",
    len(df)
)


# ---------------------------------------------------------
# Build validation features
# ---------------------------------------------------------

print()
print("Building V3 validation features...")

X_val = pd.DataFrame(
    [
        extract_features(url)
        for url in df["url_clean"]
    ],
    columns=FEATURE_NAMES
)

y_true = (
    df["label"]
    .astype(int)
    .values
)

# Binary target:
# 0 = benign
# 1 = malicious
y_binary = (
    y_true != 0
).astype(int)


# ---------------------------------------------------------
# Safety checks
# ---------------------------------------------------------

assert X_val.shape[1] == 50
assert list(X_val.columns) == FEATURE_NAMES

print(
    "Features:",
    X_val.shape[1]
)


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

print()
print("Loading V3 model...")

model = joblib.load(
    MODEL_PATH
)

assert list(model.feature_names_in_) == FEATURE_NAMES

print(
    "Model loaded:",
    MODEL_PATH
)


# ---------------------------------------------------------
# Get probabilities
# ---------------------------------------------------------

print()
print("Calculating probabilities...")

probabilities = model.predict_proba(
    X_val
)

# Class 0 = benign
benign_index = list(
    model.classes_
).index(0)

p_malicious = (
    1 -
    probabilities[:, benign_index]
)


# ---------------------------------------------------------
# Threshold analysis
# ---------------------------------------------------------

results = []

print()
print("=" * 70)
print("VALIDATION THRESHOLD RESULTS")
print("=" * 70)

print()

print(
    f"{'threshold':<12}"
    f"{'precision':<12}"
    f"{'recall':<12}"
    f"{'f1':<12}"
    f"{'false_positive_rate':<22}"
    f"{'false_negative_rate':<22}"
)

print("-" * 90)


for threshold in THRESHOLDS:

    y_pred = (
        p_malicious >= threshold
    ).astype(int)

    precision = precision_score(
        y_binary,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_binary,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_binary,
        y_pred,
        zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_binary,
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

    results.append(
        {
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "false_positive_rate": false_positive_rate,
            "false_negative_rate": false_negative_rate,
        }
    )

    print(
        f"{threshold:<12.2f}"
        f"{precision:<12.4f}"
        f"{recall:<12.4f}"
        f"{f1:<12.4f}"
        f"{false_positive_rate:<22.4f}"
        f"{false_negative_rate:<22.4f}"
    )


# ---------------------------------------------------------
# Select threshold using validation F1
# ---------------------------------------------------------

results_df = pd.DataFrame(
    results
)

best_row = results_df.loc[
    results_df["f1"].idxmax()
]


# ---------------------------------------------------------
# Final selected threshold
# ---------------------------------------------------------

print()
print("=" * 70)
print("SELECTED V3 THRESHOLD")
print("=" * 70)

print()

print(
    "Threshold:",
    f"{best_row['threshold']:.2f}"
)

print(
    "Precision:",
    f"{best_row['precision']:.4f}"
)

print(
    "Recall:",
    f"{best_row['recall']:.4f}"
)

print(
    "F1:",
    f"{best_row['f1']:.4f}"
)

print(
    "False Positive Rate:",
    f"{best_row['false_positive_rate']:.4f}"
)

print(
    "False Negative Rate:",
    f"{best_row['false_negative_rate']:.4f}"
)

print()
print("=" * 70)
print("THRESHOLD SELECTED USING VALIDATION ONLY")
print("=" * 70)

