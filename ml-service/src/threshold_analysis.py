import joblib
import pandas as pd

# 1. Load the new model. It knows its own 32 features and their order.
model = joblib.load("model/url_model.joblib")
assert list(model.classes_) == [0, 1, 2, 3], "unexpected class order"
FEATURES = list(model.feature_names_in_)

# 2. Load VALIDATION only. test.csv is never opened here.
val = pd.read_csv("data/processed/val.csv")
X_val, y_val = val[FEATURES], val["label"]

# 3. P(malicious) = 1 - P(benign). Column 0 is benign.
p_bad = 1 - model.predict_proba(X_val)[:, 0]
is_bad = (y_val != 0).to_numpy()            # True = should be blocked
n_bad, n_good = int(is_bad.sum()), int((~is_bad).sum())

print("Validation rows:", len(y_val), "| malicious:", n_bad, "| benign:", n_good)
print()
print(f"{'thr':>4} | {'bad blocked':>11} {'detect rate':>11} | "
      f"{'good blocked':>12} {'false-block':>11} | {'precision':>9}")
print("-" * 72)
for t in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]:
    blocked = p_bad >= t                     # BLOCK if P(malicious) >= t
    tp = int((blocked & is_bad).sum())       # bad URLs we blocked
    fp = int((blocked & ~is_bad).sum())      # good URLs wrongly blocked
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    print(f"{t:>4.2f} | {tp:>11} {tp / n_bad:>11.1%} | "
          f"{fp:>12} {fp / n_good:>11.1%} | {precision:>9.1%}")

print("\nThis is the VALIDATION table. Do not look at test.csv yet.")