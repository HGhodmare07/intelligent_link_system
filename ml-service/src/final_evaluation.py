import joblib
import pandas as pd

THRESHOLD = 0.80   # chosen on validation with Rule A. Do not change it after seeing test.

model = joblib.load("model/url_model.joblib")
assert list(model.classes_) == [0, 1, 2, 3]
FEATURES = list(model.feature_names_in_)

# TEST set: opened once, for this final report only.
test = pd.read_csv("data/processed/test.csv")
X_test, y_test = test[FEATURES], test["label"]

p_bad = 1 - model.predict_proba(X_test)[:, 0]     # P(malicious) = 1 - P(benign)
is_bad = (y_test != 0).to_numpy()
blocked = p_bad >= THRESHOLD

tp = int((blocked & is_bad).sum())      # bad URLs blocked
fn = int((~blocked & is_bad).sum())     # bad URLs allowed (missed)
fp = int((blocked & ~is_bad).sum())     # good URLs wrongly blocked
tn = int((~blocked & ~is_bad).sum())    # good URLs allowed

print("Test rows:", len(y_test), "| threshold:", THRESHOLD)
print(f"Malicious blocked : {tp:>6} of {tp + fn} ({tp / (tp + fn):.1%})")
print(f"Malicious allowed : {fn:>6} of {tp + fn} ({fn / (tp + fn):.1%})")
print(f"Benign wrongly blocked: {fp:>6} of {fp + tn} ({fp / (fp + tn):.1%})")
print(f"Benign allowed    : {tn:>6} of {fp + tn} ({tn / (fp + tn):.1%})")
print(f"Precision of blocks: {tp / (tp + fp):.1%}")

print("\nDetection rate by class (share blocked):")
names = {1: "defacement", 2: "phishing", 3: "malware"}
for c, n in names.items():
    m = (y_test == c).to_numpy()
    print(f"  {n:<11} {blocked[m].mean():.1%}")