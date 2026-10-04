import pandas as pd
import tldextract

# Use only the list of domain endings that comes with the package (no internet needed).
extractor = tldextract.TLDExtract(suffix_list_urls=())

def main_domain(host):
    """login.example.co.uk -> example.co.uk. IPs keep the host itself."""
    e = extractor(host)
    if e.domain and e.suffix:
        return e.domain + "." + e.suffix
    return host

# Read only the host column of each split file (nothing is changed or saved).
parts = {}
for name in ["train", "val", "test"]:
    hosts = pd.read_csv(f"data/processed/{name}.csv", usecols=["host"])["host"]
    parts[name] = hosts.fillna("").astype(str)

# Work out the main domain once per distinct host.
all_hosts = pd.concat(parts.values()).unique()
lookup = {h: main_domain(h) for h in all_hosts}

print("Examples:")
for h in ["login.example.com", "secure.example.com", "login.example.co.uk"]:
    print(f"  {h} -> {main_domain(h)}")

print("\nDistinct full hosts   :", len(all_hosts))
print("Distinct main domains :", len(set(lookup.values())))

train_hosts = set(parts["train"])
train_domains = {lookup[h] for h in train_hosts}

print("\nShare of rows whose website also appears in train:")
for name in ["val", "test"]:
    h = parts[name]
    same_host = h.isin(train_hosts).mean()
    same_domain = h.map(lookup).isin(train_domains).mean()
    print(f"  {name:<5} same full host: {same_host:6.1%} | same main domain: {same_domain:6.1%}")