from urllib.parse import urlsplit


# ---------------------------------------------------------
# Trusted legitimate domains
# ---------------------------------------------------------
# Keep this list intentionally small and exact.
# Do NOT use substring matching such as "google" in url.
TRUSTED_DOMAINS = {
    "google.com",
    "github.com",
    "microsoft.com",
    "wikipedia.org",
    "youtube.com",
}


def get_hostname(clean_url: str) -> str:
    """
    Extract hostname from a normalized URL.

    normalize_url() removes the protocol, so we temporarily
    add https:// only for correct URL parsing.
    """

    value = clean_url.strip()

    if not value:
        return ""

    parsed = urlsplit("https://" + value)

    hostname = parsed.hostname

    if hostname is None:
        return ""

    return hostname.lower().rstrip(".")


def check_reputation(clean_url: str) -> dict:
    """
    Check whether the URL belongs to a known trusted domain.

    Returns a reputation result. Unknown domains are passed
    to the ML layer.
    """

    hostname = get_hostname(clean_url)

    if not hostname:
        return {
            "trusted": False,
            "hostname": "",
            "reason": "Unable to determine hostname",
        }

    # Exact match only.
    #
    # Therefore:
    # google.com             -> trusted
    # www.google.com         -> trusted after normalization
    # google.com.evil.com    -> NOT trusted
    # google-security.com    -> NOT trusted
    # googlexc.com           -> NOT trusted
    trusted = hostname in TRUSTED_DOMAINS

    if trusted:
        return {
            "trusted": True,
            "hostname": hostname,
            "reason": "Trusted domain",
        }

    return {
        "trusted": False,
        "hostname": hostname,
        "reason": "Unknown domain",
    }