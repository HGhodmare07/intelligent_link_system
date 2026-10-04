
import math
import re
from collections import Counter


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url):
    """
    Convert a URL into one standard representation.

    IMPORTANT:
    Training and prediction must use this exact function.
    """

    url = str(url).strip().lower()

    # Decode HTML ampersand representation
    url = url.replace("&amp;", "&")

    # Remove protocol
    url = re.sub(
        r"^[a-z][a-z0-9+.-]*://",
        "",
        url
    )

    # Remove www.
    url = re.sub(
        r"^www\.",
        "",
        url
    )

    # Remove fragment
    url = url.split("#")[0]

    # Remove trailing slash
    url = url.rstrip("/")

    return url


# ============================================================
# SECURITY LISTS
# ============================================================

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "goo.gl",
    "t.co",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
    "shorturl.at",
}


SUSPICIOUS_TLDS = {
    "tk",
    "ml",
    "ga",
    "cf",
    "gq",
    "xyz",
    "top",
    "icu",
    "click",
    "work",
    "zip",
    "cn",
    "ru",
}


SUSPICIOUS_WORDS = [
    "login",
    "signin",
    "verify",
    "secure",
    "account",
    "update",
    "bank",
    "password",
    "confirm",
    "paypal",
    "webscr",
    "billing",
    "wallet",
]


EXEC_EXTENSIONS = (
    ".exe",
    ".zip",
    ".rar",
    ".apk",
    ".scr",
    ".bat",
    ".msi",
    ".jar",
)


# ============================================================
# URL PARSING
# ============================================================

def split_url(url):
    """
    Split normalized URL into:

    host
    path
    query
    rest
    has_port
    """

    match = re.search(
        r"[/?]",
        url
    )

    if match:
        host = url[:match.start()]
        rest = url[match.start():]
    else:
        host = url
        rest = ""

    # Separate query from path
    if "?" in rest:
        path, query = rest.split(
            "?",
            1
        )
    else:
        path = rest
        query = ""

    # Remove username/password portion
    host = host.split("@")[-1]

    has_port = 0

    # Detect explicit port
    if re.search(
        r":\d+$",
        host
    ):
        host = host.rsplit(
            ":",
            1
        )[0]

        has_port = 1

    return (
        host,
        path,
        query,
        rest,
        has_port
    )


# ============================================================
# ENTROPY
# ============================================================

def entropy(text):
    """
    Calculate Shannon entropy.
    """

    if not text:
        return 0.0

    counts = Counter(text)

    total = len(text)

    return -sum(
        (count / total)
        * math.log2(count / total)
        for count in counts.values()
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(url_clean):
    """
    Extract 43 URL-only features.

    36 original baseline features
    +
    7 new V2 features

    Total = 43 features.

    No live webpage access.
    No WHOIS.
    No external reputation.
    No dataset-specific phish_adv features.
    """

    url = url_clean

    (
        host,
        path,
        query,
        rest,
        has_port
    ) = split_url(url)

    # --------------------------------------------------------
    # HOST COMPONENTS
    # --------------------------------------------------------

    parts = (
        host.split(".")
        if host
        else []
    )

    # --------------------------------------------------------
    # IP ADDRESS DETECTION
    # --------------------------------------------------------

    is_ip = int(
        bool(
            re.fullmatch(
                r"\d{1,3}(\.\d{1,3}){3}",
                host
            )
        )
    )

    # --------------------------------------------------------
    # TOP LEVEL DOMAIN
    # --------------------------------------------------------

    tld = (
        parts[-1]
        if parts
        else ""
    )

    # --------------------------------------------------------
    # URL TOKENS
    # --------------------------------------------------------

    tokens = [
        token
        for token in re.split(
            r"[^a-z0-9]+",
            url
        )
        if token
    ]

    # Prevent division by zero
    n = max(
        len(url),
        1
    )

    # --------------------------------------------------------
    # URL CHARACTER COUNTS
    # --------------------------------------------------------

    digits = sum(
        ch.isdigit()
        for ch in url
    )

    letters = sum(
        ch.isalpha()
        for ch in url
    )

    # --------------------------------------------------------
    # HOST CHARACTER COUNTS
    # --------------------------------------------------------

    host_digits = sum(
        ch.isdigit()
        for ch in host
    )

    host_letters = sum(
        ch.isalpha()
        for ch in host
    )

    # ========================================================
    # NEW V2 FEATURE CALCULATIONS
    # ========================================================

    # --------------------------------------------------------
    # V2-1: Encoded character count
    #
    # Example:
    # %20
    # %3f
    # %2e
    # --------------------------------------------------------

    encoded_char_count = len(
        re.findall(
            r"%[0-9a-f]{2}",
            url
        )
    )

    # --------------------------------------------------------
    # V2-2: Numeric token count
    #
    # Example:
    # example.com/123/login
    #
    # Numeric token = 123
    # --------------------------------------------------------

    numeric_token_count = sum(
        token.isdigit()
        for token in tokens
    )

    # --------------------------------------------------------
    # V2-3: Path special characters
    # --------------------------------------------------------

    path_special = sum(
        not ch.isalnum()
        for ch in path
    )

    # --------------------------------------------------------
    # V2-4: Query special characters
    # --------------------------------------------------------

    query_special = sum(
        not ch.isalnum()
        for ch in query
    )

    # ========================================================
    # FEATURE DICTIONARY
    # ========================================================

    features = {

        # ====================================================
        # ORIGINAL 36 FEATURES
        # ====================================================

        "url_len": len(url),

        "host_len": len(host),

        "path_len": len(path),

        "query_len": len(query),

        "path_depth": path.count("/"),

        "subdomain_count": (
            0
            if is_ip
            else max(
                len(parts) - 2,
                0
            )
        ),

        "query_param_count": (
            query.count("&") + 1
            if query
            else 0
        ),

        "dot_count": url.count("."),

        "hyphen_count": url.count("-"),

        "hyphen_in_host": host.count("-"),

        "digit_count_host": host_digits,

        "at_count": url.count("@"),

        "equals_count": url.count("="),

        "percent_count": url.count("%"),

        "underscore_count": url.count("_"),

        "double_slash_in_path": int(
            "//" in rest
        ),

        "digit_ratio": (
            digits / n
        ),

        "letter_ratio": (
            letters / n
        ),

        "special_ratio": (
            len(url)
            - digits
            - letters
        ) / n,

        "url_entropy": entropy(url),

        "host_entropy": entropy(host),

        "token_count": len(tokens),

        "max_token_len": max(
            (
                len(token)
                for token in tokens
            ),
            default=0
        ),

        "avg_token_len": (
            sum(
                len(token)
                for token in tokens
            ) / len(tokens)
            if tokens
            else 0
        ),

        "is_ip_host": is_ip,

        "has_port": has_port,

        "has_punycode": int(
            "xn--" in host
        ),

        "is_shortener": int(
            host in SHORTENERS
        ),

        "suspicious_tld": int(
            tld in SUSPICIOUS_TLDS
        ),

        "tld_len": len(tld),

        "suspicious_word_count": sum(
            word in url
            for word in SUSPICIOUS_WORDS
        ),

        "has_exec_extension": int(
            path.endswith(
                EXEC_EXTENSIONS
            )
        ),

        "path_letter_ratio": (
            sum(
                ch.isalpha()
                for ch in path
            ) / len(path)
            if path
            else 0
        ),

        "path_digit_ratio": (
            sum(
                ch.isdigit()
                for ch in path
            ) / len(path)
            if path
            else 0
        ),

        "plus_count": url.count("+"),

        "path_dot_count": path.count("."),

        # ====================================================
        # NEW V2 FEATURES
        # ====================================================

        # V2-5:
        # Ratio of digits inside hostname
        "host_digit_ratio": (
            host_digits
            / max(len(host), 1)
        ),

        # V2-6:
        # Ratio of letters inside hostname
        "host_letter_ratio": (
            host_letters
            / max(len(host), 1)
        ),

        # V2-7:
        # Number of percent-encoded sequences
        "encoded_char_count":
            encoded_char_count,

        # V2-8:
        # Number of tokens made entirely of digits
        "numeric_token_count":
            numeric_token_count,

        # V2-9:
        # Hyphen density in hostname
        "host_hyphen_ratio": (
            host.count("-")
            / max(len(host), 1)
        ),

        # V2-10:
        # Special-character density in path
        "path_special_ratio": (
            path_special
            / max(len(path), 1)
        ),

        # V2-11:
        # Special-character density in query
        "query_special_ratio": (
            query_special
            / max(len(query), 1)
        ),
    }

    return features


# ============================================================
# FEATURE NAMES
# ============================================================

FEATURE_NAMES = list(
    extract_features(
        "example.com/test?id=123"
    ).keys()
)


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Number of V2 features:",
        len(FEATURE_NAMES)
    )

    print()

    print("Feature names:")

    for i, name in enumerate(
        FEATURE_NAMES,
        start=1
    ):
        print(
            f"{i:02d}. {name}"
        )

    print()

    # --------------------------------------------------------
    # TEST URLs
    # --------------------------------------------------------

    tests = [

        "https://www.wikipedia.org/",

        "http://192.168.0.1:8080/setup.exe",

        "HTTP://Secure-Login.paypal.com.example.tk/verify/account",

        "facebook.com/some.person",

        "http://example.com/login.php?user=123%20test",

    ]

    # --------------------------------------------------------
    # TEST EACH URL
    # --------------------------------------------------------

    for raw in tests:

        clean = normalize_url(raw)

        print("=" * 70)

        print(
            "RAW  :",
            raw
        )

        print(
            "CLEAN:",
            clean
        )

        feats = extract_features(
            clean
        )

        print(
            "FEATURE COUNT:",
            len(feats)
        )

        # Show non-zero values
        shown = {
            key: round(
                value,
                4
            )
            for key, value in feats.items()
            if value != 0
        }

        print(
            "NON-ZERO FEATURES:"
        )

        print(shown)

