import pandas as pd
import tldextract
from sklearn.model_selection import StratifiedGroupKFold
from features import split_url   # same host-splitting helper the features use

# Use only the domain-ending list that ships with the package (no internet).
extractor = tldextract.TLDExtract(suffix_list_urls=())

def main_domain(host):
    """login.example.co.uk -> example.co.uk. IPs keep the host itself."""
    e = extractor(host)
    if e.domain and e.suffix:
        return e.domain + "." + e.suffix
    return host

# 1. Load the feature table (read only) and add a "domain" column.
df = pd.read_csv("data/processed/features.csv")
df["host"] = [split_url(u)[0] for u in df["url_clean"]]
lookup = {h: main_domain(h) for h in df["host"].unique()}   # once per host
df["domain"] = df["host"].map(lookup)
print("Rows:", len(df), "| Main domains:", df["domain"].nunique())

# 2. Deal the domains into 5 piles, keeping class mix similar in each pile.
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
pile = pd.Series(-1, index=df.index)
for i, (_, idx) in enumerate(sgkf.split(df, df["label"], groups=df["domain"])):
    pile.iloc[idx] = i                     # rows in this pile get the number i

# 3. Pile 0 = test, pile 1 = validation, piles 2-4 = train.
test = df[pile == 0]
val = df[pile == 1]
train = df[pile >= 2]

# 4. Proof: no main domain may appear in more than one split.
d_train, d_val, d_test = set(train["domain"]), set(val["domain"]), set(test["domain"])
print("\nDomains shared train/val :", len(d_train & d_val))
print("Domains shared train/test:", len(d_train & d_test))
print("Domains shared val/test  :", len(d_val & d_test))

# 5. Save the three files.
train.to_csv("data/processed/train.csv", index=False)
val.to_csv("data/processed/val.csv", index=False)
test.to_csv("data/processed/test.csv", index=False)

# 6. Report sizes and class mix (0=benign 1=defacement 2=phishing 3=malware).
print("\nOverall class share:",
      df["label"].value_counts(normalize=True).sort_index().round(3).to_dict())
print()
for name, part in [("train", train), ("val", val), ("test", test)]:
    share = part["label"].value_counts(normalize=True).sort_index().round(3).to_dict()
    count = part["label"].value_counts().sort_index().to_dict()
    print(f"{name:<6} rows={len(part):>7} ({len(part) / len(df):.1%}) "
          f"domains={part['domain'].nunique():>6}")
    print(f"       share={share}")
    print(f"       count={count}")