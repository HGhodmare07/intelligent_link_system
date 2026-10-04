
import os
import sys
import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


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


TEST_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "test.csv"
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "model",
    "url_model_v3.joblib"
)


# ---------------------------------------------------------
# Frozen threshold
# ---------------------------------------------------------

# Selected using validation data only.
THRESHOLD = 0.30


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("FINAL V3 TEST EVALUATION")
    print("=" * 70)

    # -----------------------------------------------------
    # Load test data
    # -----------------------------------------------------

    print()
    print("Loading test dataset...")

    df = pd.read_csv(
        TEST_PATH
    )

    print(
        "Test rows:",
        len(df)
    )

    # -----------------------------------------------------
    # Build test features
    # -----------------------------------------------------

    print()
    print("Building V3 test features...")

    X_test = pd.DataFrame(
        [
            extract_features(url)
            for url in df["url_clean"]
        ],
        columns=FEATURE_NAMES
    )

    # Binary target:
    # 0 = benign
    # 1 = malicious

    y_true = (
        df["label"]
        .astype(int)
        .values
    )

    y_binary = (
        y_true != 0
    ).astype(int)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------

    assert X_test.shape[1] == 50

    assert list(
        X_test.columns
    ) == FEATURE_NAMES

    print(
        "Features:",
        X_test.shape[1]
    )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    print()
    print("Loading V3 model...")

    model = joblib.load(
        MODEL_PATH
    )

    assert list(
        model.feature_names_in_
    ) == FEATURE_NAMES

    print(
        "Model loaded:",
        MODEL_PATH
    )

    # -----------------------------------------------------
    # Probability prediction
    # -----------------------------------------------------

    print()
    print("Calculating malicious probabilities...")

    probabilities = model.predict_proba(
        X_test
    )

    benign_index = list(
        model.classes_
    ).index(0)

    # Probability that URL is malicious
    p_malicious = (
        1 -
        probabilities[:, benign_index]
    )

    # -----------------------------------------------------
    # Apply frozen threshold
    # -----------------------------------------------------

    y_pred = (
        p_malicious >= THRESHOLD
    ).astype(int)

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Final results
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL V3 TEST RESULTS")
    print("=" * 70)

    print()

    print(
        "Test rows:             ",
        len(df)
    )

    print(
        "Features:              ",
        len(FEATURE_NAMES)
    )

    print(
        "Threshold:             ",
        f"{THRESHOLD:.2f}"
    )

    print(
        "Precision:             ",
        f"{precision:.4f}"
    )

    print(
        "Recall:                ",
        f"{recall:.4f}"
    )

    print(
        "F1:                    ",
        f"{f1:.4f}"
    )

    print(
        "False Positive Rate:   ",
        f"{false_positive_rate:.4f}"
    )

    print(
        "False Negative Rate:   ",
        f"{false_negative_rate:.4f}"
    )

    # -----------------------------------------------------
    # Confusion matrix
    # -----------------------------------------------------

    print()
    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_binary,
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
    print("FINAL V3 TEST EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

