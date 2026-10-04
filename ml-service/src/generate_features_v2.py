from pathlib import Path
import pandas as pd

from .features_v2 import normalize_url, extract_features, FEATURE_NAMES

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "clean_urls.csv"
OUTPUT = ROOT / "data" / "processed" / "features_v2.csv"

clean = pd.read_csv(INPUT)
chunk_size = 10000

if not {"url_clean", "label"}.issubset(clean.columns):
    raise ValueError("Input CSV must contain url_clean and label columns")

if OUTPUT.exists():
    OUTPUT.unlink()

total = len(clean)

for start in range(0, total, chunk_size):
    chunk = clean.iloc[start:start + chunk_size]

    urls = chunk["url_clean"].astype(str)
    records = [
        extract_features(normalize_url(url))
        for url in urls
    ]

    X = pd.DataFrame(records, columns=FEATURE_NAMES)
    result = pd.DataFrame({
        "url_clean": urls.values,
        "label": chunk["label"].values
    })

    result = pd.concat([result, X], axis=1)
    result.to_csv(
        OUTPUT,
        mode="a",
        header=(start == 0),
        index=False
    )

    print(f"Processed {min(start + chunk_size, total)} / {total}")

print(f"V2 features saved to: {OUTPUT}")
print(f"Expected feature count: {len(FEATURE_NAMES)}")