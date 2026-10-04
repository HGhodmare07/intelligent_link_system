import joblib
import pandas as pd

model = joblib.load("model/url_model.joblib")
FEATURES = list(model.feature_names_in_)

# VALIDATION only. test.csv is never opened.
val = pd.read_csv("data/processed/val.csv")
val["pred"] = model.predict(val[FEATURES])

# Benign URLs (label 0) that the model called phishing (pred 2).
wrong = val[(val["label"] == 0) & (val["pred"] == 2)]
print("Benign called phishing:", len(wrong))

print("\n25 random examples:\n")
for url in wrong["url_clean"].sample(25, random_state=1):
    print(url[:100])          # cut long URLs so lines stay readable
    