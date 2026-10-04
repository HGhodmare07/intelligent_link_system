import pandas as pd

df = pd.read_csv(
    "data/raw/malicious_urls.csv",
    low_memory=False
)


def title(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


raw = df["url"].astype(str)


# ---------------------------------------------------------
# A. Normalization actions by class
# ---------------------------------------------------------
title("A. norm_actions by class (share of each class)")

table = pd.crosstab(
    df["label"],
    df["norm_actions"].fillna("none"),
    normalize="index"
)

print(table.T.round(3).to_string())


# ---------------------------------------------------------
# B. Formatting of raw URL column by class
# ---------------------------------------------------------
title("B. Formatting of the raw 'url' column")

fmt = pd.DataFrame({
    "label": df["label"],

    "has_scheme": raw.str.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://"
    ),

    "starts_www": raw.str.lower().str.startswith("www."),

    "ends_slash": raw.str.endswith("/"),

    "has_path": df["path"].notna(),

    "has_uppercase": raw.str.contains(r"[A-Z]")
})

print(
    fmt.groupby("label")
       .mean()
       .round(3)
       .to_string()
)


# ---------------------------------------------------------
# C. Check how existing features were calculated
# ---------------------------------------------------------
title("C. How were the provided columns computed?")

print(
    "url_len == len(url):",
    (
        df["url_len"] == raw.str.len()
    ).mean().round(4)
)

print(
    "url_len_v2 == len(url_normalized):",
    (
        df["url_len_v2"] == df["url_normalized"].str.len()
    ).mean().round(4)
)

print(
    "is_https == https:",
    (
        df["is_https"] == df["https"]
    ).mean().round(4)
)

print(
    "is_https == url_normalized starts with https://:",
    (
        df["is_https"]
        ==
        df["url_normalized"]
        .str.startswith("https://")
        .astype(int)
    ).mean().round(4)
)


# ---------------------------------------------------------
# D1. Reachability class by class
# ---------------------------------------------------------
title("D1. reachability_class by class")

reachability = pd.crosstab(
    df["label"],
    df["reachability_class"],
    normalize="index"
)

print(
    reachability.T.round(3).to_string()
)


# ---------------------------------------------------------
# D2. Web features by class
# ---------------------------------------------------------
title("D2. Mean of selected web_* columns by class")

web_features = [
    "web_is_live",
    "web_http_status",
    "web_forms_count",
    "web_ssl_valid",
    "web_security_score"
]

print(
    df.groupby("label")[web_features]
      .mean()
      .round(3)
      .to_string()
)


print("\n")
print("=" * 70)
print("LEAKAGE PROBE COMPLETE")
print("=" * 70)