import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, f1_score,
                             classification_report, confusion_matrix)
from features import FEATURE_NAMES   # the same 32 features, same order

# 1. Load train and validation ONLY. test.csv is never opened in this file.
train = pd.read_csv("data/processed/train.csv")
val = pd.read_csv("data/processed/val.csv")

X_train, y_train = train[FEATURE_NAMES], train["label"]
X_val, y_val = val[FEATURE_NAMES], val["label"]

print("Model type     : RandomForestClassifier (class_weight='balanced')")
print("Features       :", len(FEATURE_NAMES))
print("Training rows  :", len(train))
print("Validation rows:", len(val))

# 2. Same settings as your baseline, so only the split has changed.
model = RandomForestClassifier(
    n_estimators=100,
    min_samples_leaf=3,
    class_weight="balanced",   # rare classes count more
    n_jobs=-1,
    random_state=42,
)
print("\nTraining (2-5 minutes)...")
model.fit(X_train, y_train)

# 3. Score on validation (unseen domains).
pred = model.predict(X_val)
names = ["benign", "defacement", "phishing", "malware"]

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)
print(f"Accuracy : {accuracy_score(y_val, pred):.3f}")
print(f"Macro F1 : {f1_score(y_val, pred, average='macro'):.3f}\n")
print(classification_report(y_val, pred, target_names=names, digits=3))

print("CONFUSION MATRIX (rows = true class, columns = predicted class)")
print(pd.DataFrame(confusion_matrix(y_val, pred), index=names, columns=names).to_string())

# 4. Save the model.
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/url_model.joblib", compress=3)
print("\nSaved model to: model/url_model.joblib")