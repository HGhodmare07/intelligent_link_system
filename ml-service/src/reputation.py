import os
import math
import joblib
import pandas as pd
from urllib.parse import urlparse

from src.features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)


# Known legitimate domains for demonstration/trusted-domain handling
TRUSTED_DOMAINS = {
    "google.com",
    "www.google.com",
    "github.com",
    "www.github.com",
    "wikipedia.org",
    "www.wikipedia.org",
    "microsoft.com",
    "www.microsoft.com",
    "youtube.com",
    "www.youtube.com",
}


LOW_THRESHOLD = 0.20
HIGH_THRESHOLD = 0.90


CLASS_NAMES = {
    0: "benign",
    1: "malicious",
}


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "url_model_binary.joblib"
)


if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )


model = joblib.load(MODEL_PATH)


if not hasattr(model, "classes_"):
    raise ValueError("Model does not have classes_.")


if list(model.classes_) != [0, 1]:
    raise ValueError(
        f"Unexpected model classes: {model.classes_}"
    )


if not hasattr(model, "feature_names_in_"):
    raise ValueError(
        "Model does not contain feature_names_in_."
    )


if list(model.feature_names_in_) != list(FEATURE_NAMES):
    raise ValueError(
        "Model feature order does not match V2."
    )


if not (0 <= LOW_THRESHOLD < HIGH_THRESHOLD <= 1):
    raise ValueError("Invalid probability thresholds.")


def check_url(raw_url: str) -> dict:

    if not isinstance(raw_url, str):
        raise ValueError("URL must be a string.")

    raw_url = raw_url.strip()

    if not raw_url:
        raise ValueError("URL cannot be empty.")

    clean = normalize_url(raw_url)

    if not isinstance(clean, str) or not clean.strip():
        raise ValueError("Invalid URL.")

    clean = clean.strip()

    # ---------------------------------------------------------
    # Trusted-domain check
    # ---------------------------------------------------------

    parsed = urlparse(clean)
    host = parsed.netloc.lower().split(":")[0]

    if host in TRUSTED_DOMAINS:
        return {
            "url": raw_url,
            "normalized": clean,
            "decision": "ALLOW",
            "p_malicious": 0.0,
            "p_benign": 1.0,
            "most_likely_class": "benign",
            "low_threshold": LOW_THRESHOLD,
            "high_threshold": HIGH_THRESHOLD,
            "reason": "Trusted domain",
        }

    # ---------------------------------------------------------
    # Feature extraction
    # ---------------------------------------------------------

    feature_values = extract_features(clean)

    if isinstance(feature_values, dict):
        X = pd.DataFrame(
            [feature_values],
            columns=FEATURE_NAMES
        )
    else:
        if len(feature_values) != len(FEATURE_NAMES):
            raise ValueError(
                "Feature count does not match expected features."
            )

        X = pd.DataFrame(
            [feature_values],
            columns=FEATURE_NAMES
        )

    X = X.apply(pd.to_numeric, errors="raise")

    if X.isnull().values.any():
        raise ValueError("Missing feature values.")

    if not X.map(math.isfinite).all().all():
        raise ValueError("Non-finite feature values.")

    # ---------------------------------------------------------
    # ML prediction
    # ---------------------------------------------------------

    probabilities = model.predict_proba(X)[0]

    if len(probabilities) != len(model.classes_):
        raise ValueError("Unexpected probability output.")

    if not all(math.isfinite(float(p)) for p in probabilities):
        raise ValueError("Invalid prediction probabilities.")

    if not math.isclose(
        sum(probabilities),
        1.0,
        rel_tol=1e-5,
        abs_tol=1e-5
    ):
        raise ValueError(
            "Prediction probabilities do not sum to 1."
        )

    class_probabilities = {
        int(label): float(probability)
        for label, probability in zip(
            model.classes_,
            probabilities
        )
    }

    p_benign = class_probabilities[0]
    p_malicious = class_probabilities[1]

    predicted_index = probabilities.argmax()

    predicted_class_id = int(
        model.classes_[predicted_index]
    )

    predicted_class = CLASS_NAMES[predicted_class_id]

    # ---------------------------------------------------------
    # Security decision
    # ---------------------------------------------------------

    if p_malicious < LOW_THRESHOLD:
        decision = "ALLOW"

    elif p_malicious >= HIGH_THRESHOLD:
        decision = "BLOCK"

    else:
        decision = "REVIEW"

    return {
        "url": raw_url,
        "normalized": clean,
        "decision": decision,
        "p_malicious": round(p_malicious, 4),
        "p_benign": round(p_benign, 4),
        "most_likely_class": predicted_class,
        "low_threshold": LOW_THRESHOLD,
        "high_threshold": HIGH_THRESHOLD,
    }