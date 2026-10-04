import joblib
import pandas as pd

model = joblib.load("model/url_model.joblib")
FEATURES = list(model.feature_names_in_)

# VALIDATION only. The "domain" column was saved by split_data.py.
val = pd.read_csv("data/processed/val.csv")
val["pred"] = model.predict(val[FEATURES])

# Benign URLs (label 0) that the model called phishing (pred 2).
wrong = val[(val["label"] == 0) & (val["pred"] == 2)]
counts = wrong["domain"].value_counts()

print("Errors:", len(wrong), "| from", len(counts), "different domains")
print("Share of errors from the top 10 domains :", f"{counts.head(10).sum() / len(wrong):.1%}")
print("Share of errors from the top 100 domains:", f"{counts.head(100).sum() / len(wrong):.1%}")

print("\nTop 10 domains: errors / all validation rows of that domain")
total = val["domain"].value_counts()
for d, n in counts.head(10).items():
    print(f"  {d:<28} {n:>5} / {total[d]:>5}")