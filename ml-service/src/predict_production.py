import os
import math
import joblib
import pandas as pd

from src.features import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)

from src.reputation import check_reputation


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

THRESHOLD = 0.80

CLASS_NAMES = {
    0: "benign",
    1: "defacement",
    2: "phishing",
    3: "malware",
}


# ---------------------------------------------------------
# Model path
# ---------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "url_model.joblib"
)


if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )


# Load model once when service starts
model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# Model safety checks
# ---------------------------------------------------------

if not hasattr(model, "classes_"):
    raise ValueError("Model does not have classes_.")


if list(model.classes_) != [0, 1, 2, 3]:
    raise ValueError(
        f"Unexpected model classes: {model.classes_}"
    )


if not hasattr(model, "feature_names_in_"):
    raise ValueError(
        "Model does not contain feature_names_in_."
    )


if list(model.feature_names_in_) != list(FEATURE_NAMES):
    raise ValueError(
        "Model feature order does not match features.py."
    )


# ---------------------------------------------------------
# URL prediction
# ---------------------------------------------------------

def check_url(raw_url: str) -> dict:

    # -----------------------------------------------------
    # Input validation
    # -----------------------------------------------------

    if not isinstance(raw_url, str):
        raise ValueError("URL must be a string.")

    raw_url = raw_url.strip()

    if not raw_url:
        raise ValueError("URL cannot be empty.")

    clean = normalize_url(raw_url)

    if not isinstance(clean, str) or not clean.strip():
        raise ValueError("Invalid URL.")

    clean = clean.strip()


    # -----------------------------------------------------
    # Trusted-domain / reputation layer
    # -----------------------------------------------------

    reputation = check_reputation(clean)

    if reputation["trusted"]:

        return {
            "url": raw_url,
            "normalized": clean,
            "decision": "ALLOW",
            "p_malicious": 0.0,
            "p_benign": 1.0,
            "most_likely_class": "benign",
            "threshold": THRESHOLD,
            "reason": "Trusted domain",
            "hostname": reputation["hostname"],
        }


    # -----------------------------------------------------
    # Feature extraction
    # -----------------------------------------------------

    feature_values = extract_features(clean)

    if not isinstance(feature_values, dict):
        raise ValueError(
            "Feature extraction did not return a dictionary."
        )


    X = pd.DataFrame(
        [feature_values],
        columns=FEATURE_NAMES
    )


    # Ensure all features are numeric
    X = X.apply(pd.to_numeric, errors="raise")


    if X.isnull().values.any():
        raise ValueError(
            "Missing feature values."
        )


    if not X.map(math.isfinite).all().all():
        raise ValueError(
            "Non-finite feature values."
        )


    # -----------------------------------------------------
    # ML prediction
    # -----------------------------------------------------

    probabilities = model.predict_proba(X)[0]


    if len(probabilities) != len(model.classes_):
        raise ValueError(
            "Unexpected probability output."
        )


    if not all(
        math.isfinite(float(p))
        for p in probabilities
    ):
        raise ValueError(
            "Invalid prediction probabilities."
        )


    # Convert model output into a class → probability map
    class_probabilities = {
        int(label): float(probability)
        for label, probability in zip(
            model.classes_,
            probabilities
        )
    }


    # Class 0 = benign
    p_benign = class_probabilities[0]

    # Classes 1,2,3 = malicious
    p_malicious = (
        class_probabilities[1]
        + class_probabilities[2]
        + class_probabilities[3]
    )


    # Most likely individual class
    predicted_index = int(
        probabilities.argmax()
    )

    predicted_class_id = int(
        model.classes_[predicted_index]
    )

    predicted_class = CLASS_NAMES[
        predicted_class_id
    ]


    # -----------------------------------------------------
    # Security decision
    # -----------------------------------------------------

    if p_malicious >= THRESHOLD:
        decision = "BLOCK"
    else:
        decision = "ALLOW"


    return {
        "url": raw_url,
        "normalized": clean,
        "decision": decision,
        "p_malicious": round(
            p_malicious,
            4
        ),
        "p_benign": round(
            p_benign,
            4
        ),
        "most_likely_class": predicted_class,
        "threshold": THRESHOLD,
        "reason": "ML classification",
        "hostname": reputation["hostname"],
    }