import pandas as pd

PATH = "data/raw/malicious_urls.csv"

df = pd.read_csv(PATH, low_memory=False)


def title(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


# ---------------------------------------------------------------
# 1. MISSING VALUES
# ---------------------------------------------------------------

title("1. MISSING VALUES (only columns that have any)")

missing = df.isnull().sum()
missing = missing[missing > 0]

print(missing.to_string() if len(missing) else "None")


# ---------------------------------------------------------------
# 2. CONSTANT COLUMNS
# ---------------------------------------------------------------

title("2. CONSTANT COLUMNS")

constant = [
    c for c in df.columns
    if df[c].nunique(dropna=False) <= 1
]

print(constant if constant else "None")


# ---------------------------------------------------------------
# 3. DUPLICATE URLs
# ---------------------------------------------------------------

title("3. DUPLICATE URLs")

print(
    "Duplicate 'url' rows           :",
    df["url"].duplicated().sum()
)

print(
    "Duplicate 'url_normalized' rows:",
    df["url_normalized"].duplicated().sum()
)


# Canonical URL

canon = df["url_normalized"].str.strip().str.lower()

# Remove http:// or https://
canon = canon.str.replace(
    r"^https?://",
    "",
    regex=True
)

# Remove leading www.
canon = canon.str.replace(
    r"^www\.",
    "",
    regex=True
)

# Remove trailing slash
canon = canon.str.rstrip("/")

df["canon"] = canon

dup_rows = df["canon"].duplicated(keep=False).sum()

group_sizes = df["canon"].value_counts()

dup_groups = (group_sizes > 1).sum()

print(
    "Canonical form: rows that share a URL with another row:",
    dup_rows
)

print(
    "Canonical form: number of repeated-URL groups         :",
    dup_groups
)


# ---------------------------------------------------------------
# 4. CONFLICTING LABELS
# ---------------------------------------------------------------

title("4. CONFLICTING LABELS")

labels_per_url = (
    df.groupby("canon")["label"]
    .nunique()
)

conflict_urls = labels_per_url[
    labels_per_url > 1
].index

print(
    "URLs with conflicting labels:",
    len(conflict_urls)
)

if len(conflict_urls) > 0:

    conflicts = df[
        df["canon"].isin(conflict_urls)
    ]

    print("\nWhich label combinations conflict:")

    combos = (
        conflicts
        .groupby("canon")["label"]
        .apply(lambda s: tuple(sorted(set(s))))
    )

    print(
        combos.value_counts().to_string()
    )

    print("\n10 examples:")

    print(
        conflicts[
            ["canon", "label"]
        ]
        .sort_values("canon")
        .head(10)
        .to_string(index=False)
    )


# ---------------------------------------------------------------
# 5. TIME COLUMN
# ---------------------------------------------------------------

title("5. ts_first_seen by class")

print(
    df.groupby("label")["ts_first_seen"]
    .agg(["min", "max", "nunique"])
    .to_string()
)