
import math
import re
from collections import Counter
from urllib.parse import urlparse


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_url(url):
    url = str(url).strip().lower()
    url = url.replace("&amp;", "&")

    # Remove scheme
    url = re.sub(r"^[a-z][a-z0-9+.-]*://", "", url)

    # Remove www
    url = re.sub(r"^www\.", "", url)

    # Remove fragment
    url = url.split("#")[0]

    # Remove trailing slash
    url = url.rstrip("/")

    return url


# ============================================================
# LOOKUP SETS
# ============================================================

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "goo.gl",
    "t.co",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
    "shorturl.at",
}

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq",
    "xyz", "top", "icu", "click",
    "work", "zip", "cn", "ru",
}

SUSPICIOUS_WORDS = [
    "login",
    "signin",
    "verify",
    "secure",
    "account",
    "update",
    "bank",
    "password",
    "confirm",
    "paypal",
    "webscr",
    "billing",
    "wallet",
]

EXEC_EXTENSIONS = (
    ".exe",
    ".zip",
    ".rar",
    ".apk",
    ".scr",
    ".bat",
    ".msi",
    ".jar",
)


# ============================================================
# HELPERS
# ============================================================

def entropy(value):
    if not value:
        return 0.0

    counts = Counter(value)
    length = len(value)

    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def safe_ratio(a, b):
    return a / b if b else 0.0


def count_chars(value, chars):
    return sum(value.count(c) for c in chars)


def tokenise(value):
    return [
        token
        for token in re.split(r"[^a-zA-Z0-9]+", value)
        if token
    ]


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(url):

    clean = normalize_url(url)

    parsed = urlparse("http://" + clean)

    host = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    full = clean

    host_tokens = tokenise(host)
    path_tokens = tokenise(path)
    query_tokens = tokenise(query)

    all_tokens = tokenise(full)

    tld = host.split(".")[-1] if "." in host else ""

    # -------------------------------
    # Existing structural features
    # -------------------------------

    features = {}

    features["url_len"] = len(full)
    features["host_len"] = len(host)
    features["path_len"] = len(path)
    features["query_len"] = len(query)

    features["path_depth"] = len(
        [x for x in path.split("/") if x]
    )

    features["subdomain_count"] = max(
        len(host.split(".")) - 2,
        0
    )

    features["query_param_count"] = (
        len([x for x in query.split("&") if x])
        if query
        else 0
    )

    features["dot_count"] = full.count(".")
    features["hyphen_count"] = full.count("-")
    features["hyphen_in_host"] = host.count("-")

    features["digit_count_host"] = sum(
        c.isdigit() for c in host
    )

    features["at_count"] = full.count("@")
    features["equals_count"] = full.count("=")
    features["percent_count"] = full.count("%")
    features["underscore_count"] = full.count("_")

    features["double_slash_in_path"] = (
        1 if "//" in path else 0
    )

    features["digit_ratio"] = safe_ratio(
        sum(c.isdigit() for c in full),
        len(full)
    )

    features["letter_ratio"] = safe_ratio(
        sum(c.isalpha() for c in full),
        len(full)
    )

    features["special_ratio"] = safe_ratio(
        sum(not c.isalnum() for c in full),
        len(full)
    )

    features["url_entropy"] = entropy(full)
    features["host_entropy"] = entropy(host)

    features["token_count"] = len(all_tokens)

    token_lengths = [
        len(token)
        for token in all_tokens
    ]

    features["max_token_len"] = (
        max(token_lengths)
        if token_lengths else 0
    )

    features["avg_token_len"] = (
        sum(token_lengths) / len(token_lengths)
        if token_lengths else 0.0
    )

    features["is_ip_host"] = (
        1 if re.fullmatch(
            r"\d{1,3}(\.\d{1,3}){3}",
            host
        ) else 0
    )

    features["has_port"] = (
        1 if parsed.port else 0
    )

    features["has_punycode"] = (
        1 if "xn--" in host else 0
    )

    features["is_shortener"] = (
        1 if host in SHORTENERS else 0
    )

    features["suspicious_tld"] = (
        1 if tld in SUSPICIOUS_TLDS else 0
    )

    features["tld_len"] = len(tld)

    lower_full = full.lower()
    lower_host = host.lower()
    lower_path = path.lower()

    features["suspicious_word_count"] = sum(
        lower_full.count(word)
        for word in SUSPICIOUS_WORDS
    )

    features["suspicious_host_word_count"] = sum(
        lower_host.count(word)
        for word in SUSPICIOUS_WORDS
    )

    features["suspicious_path_word_count"] = sum(
        lower_path.count(word)
        for word in SUSPICIOUS_WORDS
    )

    features["has_exec_extension"] = (
        1 if lower_path.endswith(EXEC_EXTENSIONS)
        else 0
    )

    features["path_letter_ratio"] = safe_ratio(
        sum(c.isalpha() for c in path),
        len(path)
    )

    features["path_digit_ratio"] = safe_ratio(
        sum(c.isdigit() for c in path),
        len(path)
    )

    features["plus_count"] = full.count("+")
    features["path_dot_count"] = path.count(".")

    # -------------------------------
    # V2 structural additions
    # -------------------------------

    features["host_digit_ratio"] = safe_ratio(
        sum(c.isdigit() for c in host),
        len(host)
    )

    features["host_letter_ratio"] = safe_ratio(
        sum(c.isalpha() for c in host),
        len(host)
    )

    features["encoded_char_count"] = (
        full.count("%")
    )

    features["numeric_token_count"] = sum(
        token.isdigit()
        for token in all_tokens
    )

    features["host_hyphen_ratio"] = safe_ratio(
        host.count("-"),
        len(host)
    )

    features["path_special_ratio"] = safe_ratio(
        sum(not c.isalnum() for c in path),
        len(path)
    )

    features["query_special_ratio"] = safe_ratio(
        sum(not c.isalnum() for c in query),
        len(query)
    )

    # ========================================================
    # V3 LEXICAL FEATURES
    # ========================================================

    # Host token statistics
    features["host_token_count"] = len(host_tokens)

    host_lengths = [
        len(token)
        for token in host_tokens
    ]

    features["host_max_token_len"] = (
        max(host_lengths)
        if host_lengths else 0
    )

    features["host_avg_token_len"] = (
        sum(host_lengths) / len(host_lengths)
        if host_lengths else 0.0
    )

    # Path token statistics
    features["path_token_count"] = len(path_tokens)

    path_lengths = [
        len(token)
        for token in path_tokens
    ]

    features["path_max_token_len"] = (
        max(path_lengths)
        if path_lengths else 0
    )

    features["path_avg_token_len"] = (
        sum(path_lengths) / len(path_lengths)
        if path_lengths else 0.0
    )

    # Long hostname token
    features["has_long_host_token"] = (
        1 if any(len(token) >= 15 for token in host_tokens)
        else 0
    )

    # Long path token
    features["has_long_path_token"] = (
        1 if any(len(token) >= 20 for token in path_tokens)
        else 0
    )

    # Repeated separators
    features["repeated_hyphen"] = (
        1 if "--" in full else 0
    )

    features["repeated_dot"] = (
        1 if ".." in full else 0
    )

    features["repeated_slash"] = (
        1 if "//" in path else 0
    )

    # Host numeric/alpha structure
    features["host_digit_count"] = sum(
        c.isdigit() for c in host
    )

    features["host_special_count"] = sum(
        not c.isalnum()
        for c in host
    )

    # Path numeric/alpha structure
    features["path_digit_count"] = sum(
        c.isdigit() for c in path
    )

    features["path_special_count"] = sum(
        not c.isalnum()
        for c in path
    )

    # Query structure
    features["query_digit_count"] = sum(
        c.isdigit() for c in query
    )

    features["query_key_count"] = (
        len(query.split("&"))
        if query
        else 0
    )

    # Suspicious word combinations
    features["host_has_login_word"] = (
        1 if any(
            word in lower_host
            for word in [
                "login",
                "signin",
                "verify",
                "secure",
                "account",
            ]
        )
        else 0
    )

    features["path_has_login_word"] = (
        1 if any(
            word in lower_path
            for word in [
                "login",
                "signin",
                "verify",
                "secure",
                "account",
            ]
        )
        else 0
    )

    # Host/path separation
    features["host_path_len_ratio"] = safe_ratio(
        len(host),
        len(path)
    )

    # Character diversity
    features["unique_char_ratio"] = safe_ratio(
        len(set(full)),
        len(full)
    )

    features["host_unique_char_ratio"] = safe_ratio(
        len(set(host)),
        len(host)
    )

    features["path_unique_char_ratio"] = safe_ratio(
        len(set(path)),
        len(path)
    )

    # URL complexity
    features["separator_count"] = count_chars(
        full,
        ".-_/?:=&%@+"
    )

    features["special_token_count"] = len(
        re.findall(
            r"[^a-zA-Z0-9]+",
            full
        )
    )

    return features


# Generate feature order once
FEATURE_NAMES = list(
    extract_features("example.com").keys()
)

### Step 2 — replace `train_v3.py`

from pathlib import Path
import sys

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================
# PATH SETUP
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "src")
)

from features_v3 import (
    normalize_url,
    extract_features,
    FEATURE_NAMES,
)


# ============================================================
# FILES
# ============================================================

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VAL_FILE = ROOT / "data" / "processed" / "val.csv"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"

MODEL_FILE = ROOT / "model" / "url_model_v3.joblib"


# ============================================================
# FEATURE MATRIX
# ============================================================

def build_feature_matrix(df, name):

    print()
    print("=" * 70)
    print(f"BUILDING V3 FEATURES: {name}")
    print("=" * 70)

    rows = []

    for url in df["url_clean"]:

        clean = normalize_url(url)

        rows.append(
            extract_features(clean)
        )

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
    print("URL SECURITY MODEL V3")
    print("=" * 70)

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
    # VERIFY
    # ========================================================

    print()
    print("=" * 70)
    print("FEATURE VERIFICATION")
    print("=" * 70)

    print(
        "Total V3 features:",
        len(FEATURE_NAMES)
    )

    print(
        "Train:",
        X_train.shape
    )

    print(
        "Validation:",
        X_val.shape
    )

    print(
        "Test:",
        X_test.shape
    )

    assert X_train.shape[1] == len(FEATURE_NAMES)
    assert X_val.shape[1] == len(FEATURE_NAMES)
    assert X_test.shape[1] == len(FEATURE_NAMES)

    assert list(X_train.columns) == FEATURE_NAMES
    assert list(X_val.columns) == FEATURE_NAMES
    assert list(X_test.columns) == FEATURE_NAMES

    print("Feature verification: PASSED")

    # ========================================================
    # TRAIN
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

    print("Training completed.")

    # ========================================================
    # VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print("V3 VALIDATION")
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
    print("V3 TEST")
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
    print("TOP V3 FEATURES")
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
    # SAVE
    # ========================================================

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print()
    print("V3 model saved to:")
    print(MODEL_FILE)

    print()
    print("=" * 70)
    print("V3 TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

