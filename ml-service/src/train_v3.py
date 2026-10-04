
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# ============================================================
# PATH SETUP
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from features_v3 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)

# ============================================================
# FILE PATHS
# ============================================================

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VAL_FILE = ROOT / "data" / "processed" / "val.csv"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"

MODEL_FILE = ROOT / "model" / "url_model_v3.joblib"


# ============================================================
# FEATURE GENERATION
# ============================================================

def build_feature_matrix(df, name):

    print()
    print("=" * 70)
    print(f"Building V3 features for {name}")
    print("=" * 70)

    rows = []

    for url in df["url_clean"]:

        clean = normalize_url(url)
        features = extract_features(clean)

        rows.append(features)

    X = pd.DataFrame(
        rows,
        columns=FEATURE_NAMES
    )

    y = df["label"].astype(int)

    print("Rows:", len(X))
    print("Features:", X.shape[1])

    return X, y


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("URL SECURITY MODEL V3 TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD DATA
    # ========================================================

    print()
    print("Loading datasets...")

    train_df = pd.read_csv(
        TRAIN_FILE,
        usecols=["url_clean", "label"]
    )

    val_df = pd.read_csv(
        VAL_FILE,
        usecols=["url_clean", "label"]
    )

    test_df = pd.read_csv(
        TEST_FILE,
        usecols=["url_clean", "label"]
    )

    print()
    print("Train:", train_df.shape)
    print("Validation:", val_df.shape)
    print("Test:", test_df.shape)

    # ========================================================
    # BUILD FEATURES
    # ========================================================

    X_train, y_train = build_feature_matrix(
        train_df,
        "TRAIN"
    )

    X_val, y_val = build_feature_matrix(
        val_df,
        "VALIDATION"
    )

    X_test, y_test = build_feature_matrix(
        test_df,
        "TEST"
    )

    # ========================================================
    # VERIFY FEATURES
    # ========================================================

    print()
    print("=" * 70)
    print("FEATURE VERIFICATION")
    print("=" * 70)

    print("Total V3 features:", len(FEATURE_NAMES))

    print("Train:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Test:", X_test.shape)

    assert list(X_train.columns) == FEATURE_NAMES
    assert list(X_val.columns) == FEATURE_NAMES
    assert list(X_test.columns) == FEATURE_NAMES

    print()
    print("Feature verification: PASSED")

    # ========================================================
    # TRAIN RANDOM FOREST
    # ========================================================

    print()
    print("=" * 70)
    print("TRAINING RANDOM FOREST V3")
    print("=" * 70)

    model = RandomForestClassifier(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
        max_features="sqrt",
        min_samples_leaf=3,
    )

    model.fit(
        X_train,
        y_train
    )

    print()
    print("Training completed.")

    # ========================================================
    # VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print("V3 VALIDATION RESULTS")
    print("=" * 70)

    val_pred = model.predict(X_val)

    print(
        classification_report(
            y_val,
            val_pred,
            target_names=[
                "benign",
                "defacement",
                "phishing",
                "malware",
            ],
            digits=4,
            zero_division=0,
        )
    )

    print("Validation confusion matrix:")

    print(
        confusion_matrix(
            y_val,
            val_pred
        )
    )

    # ========================================================
    # TEST
    # ========================================================

    print()
    print("=" * 70)
    print("V3 TEST RESULTS")
    print("=" * 70)

    test_pred = model.predict(X_test)

    print(
        classification_report(
            y_test,
            test_pred,
            target_names=[
                "benign",
                "defacement",
                "phishing",
                "malware",
            ],
            digits=4,
            zero_division=0,
        )
    )

    print("Test confusion matrix:")

    print(
        confusion_matrix(
            y_test,
            test_pred
        )
    )

    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    print()
    print("=" * 70)
    print("TOP V3 FEATURE IMPORTANCE")
    print("=" * 70)

    importance = pd.Series(
        model.feature_importances_,
        index=FEATURE_NAMES
    ).sort_values(
        ascending=False
    )

    for i, (feature, value) in enumerate(
        importance.head(25).items(),
        start=1
    ):

        print(
            f"{i:02d}. "
            f"{feature:<35} "
            f"{value:.6f}"
        )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    print()
    print("=" * 70)
    print("SAVING V3 MODEL")
    print("=" * 70)

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print()
    print("Model saved to:")
    print(MODEL_FILE)

    print()
    print("=" * 70)
    print("V3 TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

