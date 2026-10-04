import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEST_FILE = ROOT / "data" / "processed" / "test.csv"
TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VAL_FILE = ROOT / "data" / "processed" / "val.csv"

print("=" * 70)
print("DOMAIN LABEL CONFLICT AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

train = pd.read_csv(
    TRAIN_FILE,
    usecols=["url_clean", "host", "domain", "label"]
)

val = pd.read_csv(
    VAL_FILE,
    usecols=["url_clean", "host", "domain", "label"]
)

test = pd.read_csv(
    TEST_FILE,
    usecols=["url_clean", "host", "domain", "label"]
)

df = pd.concat(
    [train, val, test],
    ignore_index=True
)

print()
print("Total rows:", len(df))
print("Unique domains:", df["domain"].nunique())

# ------------------------------------------------------------
# FIND DOMAINS WITH MULTIPLE LABELS
# ------------------------------------------------------------

domain_labels = (
    df.groupby("domain")["label"]
    .nunique()
    .sort_values(ascending=False)
)

conflicting_domains = domain_labels[
    domain_labels > 1
]

print()
print("Domains with multiple labels:", len(conflicting_domains))

# ------------------------------------------------------------
# LABEL DISTRIBUTION FOR CONFLICTING DOMAINS
# ------------------------------------------------------------

conflict_df = df[
    df["domain"].isin(conflicting_domains.index)
].copy()

summary = (
    conflict_df
    .groupby("domain")["label"]
    .value_counts()
    .unstack(fill_value=0)
)

print()
print("Top conflicting domains by number of URLs:")

summary["total"] = summary.sum(axis=1)

print(
    summary
    .sort_values("total", ascending=False)
    .head(30)
    .to_string()
)

# ------------------------------------------------------------
# EXAMPLES
# ------------------------------------------------------------

print()
print("=" * 70)
print("EXAMPLES OF CONFLICTING DOMAINS")
print("=" * 70)

top_domains = (
    summary
    .sort_values("total", ascending=False)
    .head(10)
    .index
)

for domain in top_domains:

    print()
    print("-" * 70)
    print("DOMAIN:", domain)

    rows = df[
        df["domain"] == domain
    ][
        ["url_clean", "label"]
    ].head(15)

    print(
        rows.to_string(index=False)
    )

# ------------------------------------------------------------
# ERROR DOMAINS
# ------------------------------------------------------------

ERROR_FILE = ROOT / "data" / "processed" / "v2_errors.csv"

errors = pd.read_csv(ERROR_FILE)

errors["domain"] = (
    errors["url_clean"]
    .str.split("/")
    .str[0]
    .str.lower()
)

error_domains = (
    errors
    .groupby("domain")
    .size()
    .sort_values(ascending=False)
)

print()
print("=" * 70)
print("TOP V2 ERROR DOMAINS")
print("=" * 70)

print(
    error_domains
    .head(30)
    .to_string()
)

print()
print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)