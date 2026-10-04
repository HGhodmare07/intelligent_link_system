import os
import joblib
import pandas as pd

from features import FEATURE_NAMES
from sklearn.metrics import confusion_matrix


# --------------------------------
# Paths
# --------------------------------

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


# --------------------------------
# Load model and validation data
# --------------------------------

model = joblib.load(MODEL_PATH)

df = pd.read_csv(VAL_PATH)

X = df[FEATURE_NAMES]

# 0 = benign
# 1 = malicious
y_true = (df["label"] != 0).astype(int)


# --------------------------------
# Malicious probability
# --------------------------------

probabilities = model.predict_proba(X)

classes = list(model.classes_)

benign_index = classes.index(0)

p_malicious = (
    1.0 - probabilities[:, benign_index]
)


# --------------------------------
# Evaluate decision bands
# --------------------------------

threshold_pairs = [
    (0.10, 0.80),
    (0.15, 0.80),
    (0.20, 0.80),
    (0.20, 0.85),
    (0.20, 0.90),
    (0.25, 0.80),
    (0.25, 0.85),
    (0.25, 0.90),
    (0.30, 0.80),
    (0.30, 0.85),
    (0.30, 0.90),
    (0.35, 0.80),
    (0.35, 0.85),
    (0.35, 0.90),
    (0.40, 0.80),
    (0.40, 0.85),
    (0.40, 0.90),
]


results = []


for low_threshold, high_threshold in threshold_pairs:

    # --------------------------------
    # Decision
    # --------------------------------

    decisions = []

    for probability in p_malicious:

        if probability < low_threshold:
            decisions.append("ALLOW")

        elif probability >= high_threshold:
            decisions.append("BLOCK")

        else:
            decisions.append("REVIEW")


    decisions = pd.Series(decisions)


    # --------------------------------
    # High-confidence BLOCK metrics
    # --------------------------------

    block_mask = decisions == "BLOCK"

    if block_mask.sum() > 0:

        block_actual_malicious = (
            y_true[block_mask] == 1
        ).sum()

        block_actual_benign = (
            y_true[block_mask] == 0
        ).sum()

        block_precision = (
            block_actual_malicious
            / block_mask.sum()
        )

    else:

        block_actual_malicious = 0
        block_actual_benign = 0
        block_precision = 0


    # --------------------------------
    # ALLOW metrics
    # --------------------------------

    allow_mask = decisions == "ALLOW"

    if allow_mask.sum() > 0:

        allow_actual_benign = (
            y_true[allow_mask] == 0
        ).sum()

        allow_actual_malicious = (
            y_true[allow_mask] == 1
        ).sum()

        allow_safety = (
            allow_actual_benign
            / allow_mask.sum()
        )

    else:

        allow_actual_benign = 0
        allow_actual_malicious = 0
        allow_safety = 0


    # --------------------------------
    # REVIEW size
    # --------------------------------

    review_mask = decisions == "REVIEW"

    review_count = review_mask.sum()

    review_percentage = (
        review_count / len(df)
    )


    # --------------------------------
    # Overall automatic decisions
    # --------------------------------

    automatic_count = (
        allow_mask.sum()
        + block_mask.sum()
    )

    automatic_percentage = (
        automatic_count / len(df)
    )


    results.append({

        "low_threshold": low_threshold,

        "high_threshold": high_threshold,

        "allow_count": int(
            allow_mask.sum()
        ),

        "review_count": int(
            review_count
        ),

        "block_count": int(
            block_mask.sum()
        ),

        "review_percentage": round(
            review_percentage,
            4
        ),

        "automatic_percentage": round(
            automatic_percentage,
            4
        ),

        "allow_safety": round(
            allow_safety,
            4
        ),

        "block_precision": round(
            block_precision,
            4
        ),

    })


# --------------------------------
# Display
# --------------------------------

results_df = pd.DataFrame(results)

print("\nDECISION BAND ANALYSIS")
print("=" * 100)

print(
    results_df.to_string(
        index=False
    )
)

print("\nDefinitions:")
print(
    "allow_safety = percentage of ALLOW decisions "
    "that are actually benign."
)

print(
    "block_precision = percentage of BLOCK decisions "
    "that are actually malicious."
)

print(
    "review_percentage = percentage of URLs sent to REVIEW."
)

print(
    "automatic_percentage = percentage handled automatically "
    "by ALLOW or BLOCK."
)