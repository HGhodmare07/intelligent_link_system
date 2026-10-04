
import os
import joblib
import pandas as pd

from src.features_v2 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)


LOW_THRESHOLD = 0.20
HIGH_THRESHOLD = 0.90


CLASS_NAMES = {
    0: "benign",
    1: "malicious",
}


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "url_model_binary.joblib"
)


model = joblib.load(MODEL_PATH)


assert list(model.classes_) == [0, 1], (
    f"Unexpected model classes: {model.classes_}"
)

assert list(model.feature_names_in_) == FEATURE_NAMES, (
    "Model feature order does not match V2 feature order."
)


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

    p_benign = float(
        probabilities[
            list(model.classes_).index(0)
        ]
    )

    p_malicious = float(
        probabilities[
            list(model.classes_).index(1)
        ]
    )

    predicted_index = int(
        probabilities.argmax()
    )

    predicted_class = CLASS_NAMES[predicted_index]

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

