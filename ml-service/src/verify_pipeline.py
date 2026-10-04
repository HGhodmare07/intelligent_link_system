import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .features_v2 import FEATURE_NAMES

# Run this script from the ml-service folder
ROOT = Path.cwd()

# File paths
clean_path = ROOT / "data" / "processed" / "clean_urls.csv"
features_path = ROOT / "data" / "processed" / "features_v2.csv"
model_path = ROOT / "model" / "url_model_binary.joblib"

# Check required files exist
for path in (clean_path, features_path, model_path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

# Load datasets
clean = pd.read_csv(clean_path)
feat = pd.read_csv(features_path)

print("=" * 50)
print("       V2 PIPELINE VERIFICATION")
print("=" * 50)

print("clean_urls.csv rows :", len(clean))
print("features_v2.csv rows:", len(feat))

# Check same URLs and labels in same order
same_urls = (
    clean["url_clean"].astype(str).values
    == feat["url_clean"].astype(str).values
).all()

same_labels = (
    clean["label"].values == feat["label"].values
).all()

print("\nSame URLs in same order:", same_urls)
print("Same labels            :", same_labels)

# Check row counts
print("Same row count         :", len(clean) == len(feat))

# Check required V2 feature columns
missing = [name for name in FEATURE_NAMES if name not in feat.columns]

if missing:
    raise ValueError(f"Missing V2 feature columns: {missing}")

# Select V2 features in exact expected order
X = feat[FEATURE_NAMES]

print("\nExpected feature count :", len(FEATURE_NAMES))
print("Actual feature count   :", X.shape[1])

# Check NaN and infinite values
print("NaN cells              :", int(X.isnull().sum().sum()))

X_numeric = X.to_numpy(dtype=float)
print("Infinite cells         :", int(np.isinf(X_numeric).sum()))

# Check saved model
model = joblib.load(model_path)

print("\nModel n_features_in_ :", model.n_features_in_)
print("Model feature count  :", len(FEATURE_NAMES))

if model.n_features_in_ != len(FEATURE_NAMES):
    print("ERROR: Model feature count does not match V2!")
else:
    print("Model feature count matches: True")

# Check feature order
model_features = getattr(model, "feature_names_in_", None)

if model_features is not None:
    order_matches = list(model_features) == FEATURE_NAMES
    print("Feature order matches:", order_matches)
else:
    order_matches = None
    print("Model has no feature_names_in_ attribute.")
    print("Verify feature order against the training code.")

# File timestamps
print("\nFile timestamps:")

for path in (clean_path, features_path, model_path):
    print(
        f"{str(path.relative_to(ROOT)):<40}",
        pd.Timestamp(os.path.getmtime(path), unit="s")
    )

# Final verification summary
print("\n" + "=" * 50)

checks = [
    same_urls,
    same_labels,
    len(clean) == len(feat),
    X.isnull().sum().sum() == 0,
    np.isfinite(X_numeric).all(),
    model.n_features_in_ == len(FEATURE_NAMES),
]

if order_matches is not None:
    checks.append(order_matches)

if all(checks):
    print("All verification checks PASSED.")
else:
    print("Verification FAILED. Check the results above.")

print("=" * 50)