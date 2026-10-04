
import os
import joblib
import pandas as pd

from features_v3 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)


CLASS_NAMES = {
    0: "benign",
    1: "defacement",
    2: "phishing",
    3: "malware",
}


# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "url_model_v3.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# VERIFY MODEL
# ============================================================

assert list(model.classes_) == [0, 1, 2, 3]

assert list(model.feature_names_in_) == FEATURE_NAMES, (
    "V3 model feature order does not match features_v3.py"
)


# ============================================================
# PREDICT URL
# ============================================================

def check_url(raw_url: str):

    if not isinstance(raw_url, str):
        raise ValueError("URL must be a string.")

    raw_url = raw_url.strip()

    if not raw_url:
        raise ValueError("URL cannot be empty.")

    clean = normalize_url(raw_url)

    if not clean:
        raise ValueError("Invalid URL.")

    feature_values = extract_features(clean)

    X = pd.DataFrame(
        [feature_values],
        columns=FEATURE_NAMES
    )

    probabilities = model.predict_proba(X)[0]

    benign_index = list(
        model.classes_
    ).index(0)

    p_benign = float(
        probabilities[benign_index]
    )

    p_malicious = 1.0 - p_benign

    predicted_index = int(
        probabilities.argmax()
    )

    predicted_class = CLASS_NAMES[
        predicted_index
    ]

    return {
        "url": raw_url,
        "normalized": clean,
        "p_malicious": round(
            p_malicious,
            4
        ),
        "p_benign": round(
            p_benign,
            4
        ),
        "most_likely_class": predicted_class,
    }

