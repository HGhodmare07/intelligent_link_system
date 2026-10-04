import math
import re
from collections import Counter


# ------------------------------------------------------------------
# 1. NORMALIZER
# ------------------------------------------------------------------
def normalize_url(url):
    """Turn any URL into one standard form (used in training AND prediction)."""
    url = str(url).strip().lower()
    url = url.replace("&amp;", "&")
    url = re.sub(r"^[a-z][a-z0-9+.-]*://", "", url)
    url = re.sub(r"^www\.", "", url)
    url = url.split("#")[0]
    url = url.rstrip("/")
    return url


# ------------------------------------------------------------------
# 2. SMALL LOOKUP LISTS
# ------------------------------------------------------------------
SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
    "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "shorturl.at"
}

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "icu",
    "click", "work", "zip", "cn", "ru"
}

SUSPICIOUS_WORDS = [
    "login", "signin", "verify", "secure", "account", "update",
    "bank", "password", "confirm", "paypal", "webscr",
    "billing", "wallet"
]

EXEC_EXTENSIONS = (
    ".exe", ".zip", ".rar", ".apk",
    ".scr", ".bat", ".msi", ".jar"
)


# ------------------------------------------------------------------
# 3. HELPERS
# ------------------------------------------------------------------
def split_url(url):
    """Split normalized URL into host, path, query, rest, has_port."""
    m = re.search(r"[/?]", url)

    if m:
        host, rest = url[:m.start()], url[m.start():]
    else:
        host, rest = url, ""

    if "?" in rest:
        path, query = rest.split("?", 1)
    else:
        path, query = rest, ""

    host = host.split("@")[-1]

    has_port = 0

    if re.search(r":\d+$", host):
        host = host.rsplit(":", 1)[0]
        has_port = 1

    return host, path, query, rest, has_port


def entropy(text):
    """Shannon entropy: how random the characters look."""
    if not text:
        return 0.0

    counts = Counter(text)
    total = len(text)

    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values()
    )


def count_suspicious_words(text):
    """Count suspicious keywords appearing in a piece of URL text."""
    return sum(word in text for word in SUSPICIOUS_WORDS)


# ------------------------------------------------------------------
# 4. FEATURE EXTRACTION
# ------------------------------------------------------------------
def extract_features(url_clean):
    """Take ONE normalized URL and return a dict of numeric features."""

    url = url_clean

    host, path, query, rest, has_port = split_url(url)

    parts = host.split(".") if host else []

    is_ip = int(
        bool(
            re.fullmatch(
                r"\d{1,3}(\.\d{1,3}){3}",
                host
            )
        )
    )

    tld = parts[-1] if parts else ""

    tokens = [
        t for t in re.split(r"[^a-z0-9]+", url)
        if t
    ]

    n = max(len(url), 1)

    digits = sum(ch.isdigit() for ch in url)
    letters = sum(ch.isalpha() for ch in url)

    # New contextual keyword features
    suspicious_host_words = count_suspicious_words(host)
    suspicious_path_words = count_suspicious_words(path)

    return {

        # ----------------------------------------------------------
        # LENGTHS
        # ----------------------------------------------------------
        "url_len": len(url),
        "host_len": len(host),
        "path_len": len(path),
        "query_len": len(query),

        # ----------------------------------------------------------
        # STRUCTURE
        # ----------------------------------------------------------
        "path_depth": path.count("/"),

        "subdomain_count": (
            0 if is_ip
            else max(len(parts) - 2, 0)
        ),

        "query_param_count": (
            query.count("&") + 1
            if query else 0
        ),

        # ----------------------------------------------------------
        # CHARACTER COUNTS
        # ----------------------------------------------------------
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "hyphen_in_host": host.count("-"),
        "digit_count_host": sum(ch.isdigit() for ch in host),
        "at_count": url.count("@"),
        "equals_count": url.count("="),
        "percent_count": url.count("%"),
        "underscore_count": url.count("_"),

        "double_slash_in_path": int("//" in rest),

        # ----------------------------------------------------------
        # RATIOS AND RANDOMNESS
        # ----------------------------------------------------------
        "digit_ratio": digits / n,
        "letter_ratio": letters / n,

        "special_ratio": (
            len(url) - digits - letters
        ) / n,

        "url_entropy": entropy(url),
        "host_entropy": entropy(host),

        # ----------------------------------------------------------
        # TOKENS
        # ----------------------------------------------------------
        "token_count": len(tokens),

        "max_token_len": max(
            (len(t) for t in tokens),
            default=0
        ),

        "avg_token_len": (
            sum(len(t) for t in tokens) / len(tokens)
            if tokens
            else 0
        ),

        # ----------------------------------------------------------
        # HOST FLAGS
        # ----------------------------------------------------------
        "is_ip_host": is_ip,
        "has_port": has_port,
        "has_punycode": int("xn--" in host),
        "is_shortener": int(host in SHORTENERS),
        "suspicious_tld": int(tld in SUSPICIOUS_TLDS),
        "tld_len": len(tld),

        # ----------------------------------------------------------
        # KEYWORDS
        # ----------------------------------------------------------
        # Keep the old feature for baseline compatibility.
        "suspicious_word_count": count_suspicious_words(url),

        # NEW: contextual keyword features.
        "suspicious_host_word_count": suspicious_host_words,
        "suspicious_path_word_count": suspicious_path_words,

        # ----------------------------------------------------------
        # FILE / PAYLOAD INDICATOR
        # ----------------------------------------------------------
        "has_exec_extension": int(
            path.endswith(EXEC_EXTENSIONS)
        ),

        # ----------------------------------------------------------
        # PATH SHAPE
        # ----------------------------------------------------------
        "path_letter_ratio": (
            sum(ch.isalpha() for ch in path) / len(path)
            if path
            else 0
        ),

        "path_digit_ratio": (
            sum(ch.isdigit() for ch in path) / len(path)
            if path
            else 0
        ),

        "plus_count": url.count("+"),
        "path_dot_count": path.count("."),
    }


# ------------------------------------------------------------------
# 5. FEATURE ORDER
# ------------------------------------------------------------------
# The model must always receive features in exactly this same order.
FEATURE_NAMES = list(
    extract_features("example.com").keys()
)


# ------------------------------------------------------------------
# 6. SELF-TEST
# ------------------------------------------------------------------
if __name__ == "__main__":

    print("Number of features:", len(FEATURE_NAMES))
    print("\nFeature names:")
    for i, name in enumerate(FEATURE_NAMES, start=1):
        print(f"{i:2}. {name}")

    print("\n" + "=" * 70)

    tests = [
        "br-icloud.com.br",
        "http://192.168.0.1:8080/login.php?user=a&amp;pass=b",
        "HTTP://Secure-Login.paypal.com.example.tk/verify/account",
        "spokeo.com/joan+donley",
    ]

    for raw in tests:

        clean = normalize_url(raw)

        print("\nRAW  :", raw)
        print("CLEAN:", clean)

        feats = extract_features(clean)

        shown = {
            k: round(v, 3)
            for k, v in feats.items()
            if v != 0
        }

        print("NON-ZERO FEATURES:")
        print(shown)