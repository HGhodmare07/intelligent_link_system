import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ERROR_FILE = ROOT / "data" / "processed" / "v2_errors.csv"

df = pd.read_csv(ERROR_FILE)

print("=" * 70)
print("V2 ERROR PATTERN ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# BASIC ERROR DISTRIBUTION
# ------------------------------------------------------------

print()
print("Error types:")
print(df["error_type"].value_counts())

print()
print("Errors by actual label:")
print(
    df.groupby(
        ["error_type", "label"]
    ).size()
)

# ------------------------------------------------------------
# ERROR PROBABILITY RANGES
# ------------------------------------------------------------

print()
print("=" * 70)
print("FALSE NEGATIVE PROBABILITY")
print("=" * 70)

fn = df[
    df["error_type"] == "FALSE_NEGATIVE"
]

print(
    fn["p_malicious"].describe(
        percentiles=[
            0.01,
            0.05,
            0.10,
            0.25,
            0.50,
            0.75,
        ]
    )
)

print()
print("=" * 70)
print("FALSE POSITIVE PROBABILITY")
print("=" * 70)

fp = df[
    df["error_type"] == "FALSE_POSITIVE"
]

print(
    fp["p_malicious"].describe(
        percentiles=[
            0.01,
            0.05,
            0.10,
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
        ]
    )
)

# ------------------------------------------------------------
# ERROR DOMAINS BY LABEL
# ------------------------------------------------------------

print()
print("=" * 70)
print("TOP FALSE NEGATIVE DOMAINS BY LABEL")
print("=" * 70)

fn["domain"] = (
    fn["url_clean"]
    .str.split("/")
    .str[0]
    .str.lower()
)

for label in sorted(fn["label"].unique()):

    subset = fn[
        fn["label"] == label
    ]

    print()
    print("LABEL:", label)
    print("Count:", len(subset))

    print(
        subset["domain"]
        .value_counts()
        .head(20)
        .to_string()
    )

# ------------------------------------------------------------
# FALSE POSITIVE LABELS
# ------------------------------------------------------------

print()
print("=" * 70)
print("FALSE POSITIVES")
print("=" * 70)

fp["domain"] = (
    fp["url_clean"]
    .str.split("/")
    .str[0]
    .str.lower()
)

print()
print("False positives by actual label:")
print(
    fp["label"]
    .value_counts()
    .sort_index()
)

print()
print("Top false-positive domains:")

print(
    fp["domain"]
    .value_counts()
    .head(30)
    .to_string()
)

# ------------------------------------------------------------
# URL STRUCTURE OF ERRORS
# ------------------------------------------------------------

print()
print("=" * 70)
print("URL STRUCTURE")
print("=" * 70)

df["url_len"] = df["url_clean"].str.len()

df["path_len"] = (
    df["url_clean"]
    .str.split("/", n=1)
    .str[1]
    .fillna("")
    .str.len()
)

df["has_query"] = (
    df["url_clean"]
    .str.contains("?", regex=False)
)

df["has_ip"] = (
    df["url_clean"]
    .str.match(
        r"^\d{1,3}(\.\d{1,3}){3}"
    )
)

print()
print(
    df.groupby("error_type")[
        [
            "url_len",
            "path_len",
            "has_query",
            "has_ip",
        ]
    ]
    .mean()
    .round(4)
)

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)