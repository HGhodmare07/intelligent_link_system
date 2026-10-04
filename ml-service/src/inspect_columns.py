import pandas as pd

# Path is relative to where you run the command (the project root).
PATH = "data/raw/malicious_urls.csv"

# low_memory=False makes pandas read the whole file before guessing
# column types. This avoids "mixed type" warnings on a wide CSV.
df = pd.read_csv(PATH, low_memory=False)

print("=" * 70)
print("SHAPE (rows, columns):", df.shape)
print("=" * 70)

# Show pandas' guess at each column: position, name, type,
# number of distinct values, and the first value as an example.
print(f"{'#':>3}  {'column':<35} {'dtype':<10} {'unique':>8}  first value")
print("-" * 90)
for i, col in enumerate(df.columns):
    first = str(df[col].iloc[0])[:40]  # cut long strings so lines stay readable
    print(f"{i:>3}  {col:<35} {str(df[col].dtype):<10} {df[col].nunique():>8}  {first}")

# A label column has very few distinct values (you said 4 classes).
# Columns with <= 4 unique values are candidates for "the label".
print()
print("=" * 70)
print("COLUMNS WITH 4 OR FEWER UNIQUE VALUES (label candidates)")
print("=" * 70)
for col in df.columns:
    if df[col].nunique() <= 4:
        print(col, "->", df[col].value_counts(dropna=False).to_dict())

# A URL column is text (dtype 'object'). List all text columns.
print()
print("=" * 70)
print("TEXT COLUMNS (URL column candidates) with 3 sample values")
print("=" * 70)
for col in df.select_dtypes(include="object").columns:
    print(col, "->", df[col].head(3).tolist())