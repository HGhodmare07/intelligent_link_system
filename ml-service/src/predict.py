import joblib
import pandas as pd
from features import normalize_url, extract_features, FEATURE_NAMES

THRESHOLD = 0.80   # chosen on validation, confirmed once on test. Do not change.
CLASS_NAMES = {0: "benign", 1: "defacement", 2: "phishing", 3: "malware"}

# Load the model ONCE when this file is imported, not on every request.
model = joblib.load("model/url_model.joblib")
assert list(model.classes_) == [0, 1, 2, 3]
assert list(model.feature_names_in_) == FEATURE_NAMES, "feature order mismatch"


def check_url(raw_url):
    """Take any URL a user typed and return an ALLOW/BLOCK decision."""
    clean = normalize_url(raw_url)
    if clean == "":
        raise ValueError("empty URL")

    # One-row table with the columns in the exact order the model was trained on.
    X = pd.DataFrame([extract_features(clean)], columns=FEATURE_NAMES)

    probs = model.predict_proba(X)[0]          # [benign, defacement, phishing, malware]
    p_malicious = 1 - probs[0]                 # P(malicious) = 1 - P(benign)
    top_class = CLASS_NAMES[int(probs.argmax())]

    return {
        "url": raw_url,
        "normalized": clean,
        "decision": "BLOCK" if p_malicious >= THRESHOLD else "ALLOW",
        "p_malicious": round(float(p_malicious), 3),
        "most_likely_class": top_class,
    }


# Quick self-test when you run this file directly.
if __name__ == "__main__":
    for u in ["https://www.wikipedia.org/",
              "http://192.168.0.1:8080/setup.exe",
              "HTTP://Secure-Login.paypal.com.example.tk/verify/account",
              "facebook.com/some.person"]:
        print(check_url(u))