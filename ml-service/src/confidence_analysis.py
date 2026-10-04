import os
import joblib
import pandas as pd

from features import FEATURE_NAMES


# -----------------------------
# Paths
# -----------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "url_model.joblib"
)

VAL_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "val.csv"
)


# -----------------------------
# Load model and validation data
# -----------------------------

model = joblib.load(MODEL_PATH)

df = pd.read_csv(VAL_PATH)


# -----------------------------
# Prepare features
# -----------------------------

X = df[FEATURE_NAMES]
y = (df["label"] != 0).astype(int)


# -----------------------------
# Get malicious probability
# -----------------------------

probabilities = model.predict_proba(X)

classes = list(model.classes_)

benign_index = classes.index(0)

p_malicious = 1.0 - probabilities[:, benign_index]

df["p_malicious"] = p_malicious


# -----------------------------
# Create probability bands
# -----------------------------

bins = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0
]

labels = [
    "0.0-0.1",
    "0.1-0.2",
    "0.2-0.3",
    "0.3-0.4",
    "0.4-0.5",
    "0.5-0.6",
    "0.6-0.7",
    "0.7-0.8",
    "0.8-0.9",
    "0.9-1.0"
]

df["probability_band"] = pd.cut(
    df["p_malicious"],
    bins=bins,
    labels=labels,
    include_lowest=True
)


# -----------------------------
# Analyze each band
# -----------------------------

results = []

for band, group in df.groupby(
    "probability_band",
    observed=False
):

    total = len(group)

    actual_malicious = int(
        group["label"].ne(0).sum()
    )

    actual_benign = total - actual_malicious

    malicious_rate = (
        actual_malicious / total
        if total > 0
        else 0
    )

    results.append({
        "probability_band": str(band),
        "total": total,
        "actual_malicious": actual_malicious,
        "actual_benign": actual_benign,
        "malicious_rate": round(
            malicious_rate,
            4
        )
    })


results_df = pd.DataFrame(results)


# -----------------------------
# Display results
# -----------------------------

print("\nMODEL CONFIDENCE BAND ANALYSIS")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)

print("\nInterpretation:")
print(
    "malicious_rate = percentage of URLs in that probability "
    "band that are actually malicious."
)