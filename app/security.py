import ipaddress
import os
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000"))
MAX_TOP_K = int(os.getenv("MAX_TOP_K", "20"))
MAX_CSV_BYTES = int(os.getenv("MAX_CSV_BYTES", str(5 * 1024 * 1024)))


def is_safe_http_url(url):
    if not url or not isinstance(url, str):
        return False

    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.netloc:
        return False
    if parsed.username or parsed.password:
        return False

    host = parsed.hostname
    if not host:
        return False

    lowered = host.lower()
    if lowered in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    if lowered.endswith(".local") or lowered.endswith(".internal"):
        return False

    try:
        ip = ipaddress.ip_address(lowered)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        ):
            return False
    except ValueError:
        pass

    port = parsed.port
    if port is not None and port not in (80, 443):
        return False

    return True


def is_amazon_url(url):
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    return host == "amazon.com" or host.endswith(".amazon.com")


def resolve_project_csv_path(csv_path):
    if not csv_path or not isinstance(csv_path, str):
        raise ValueError("Invalid CSV path")

    candidate = Path(csv_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    resolved = candidate.resolve()
    root = PROJECT_ROOT.resolve()

    if root not in resolved.parents and resolved != root:
        raise ValueError("CSV path must stay within the project directory")

    if resolved.suffix.lower() != ".csv":
        raise ValueError("CSV path must point to a .csv file")

    if not resolved.exists():
        raise ValueError("CSV file not found")

    return resolved


def clamp_top_k(value):
    try:
        top_k = int(value)
    except (TypeError, ValueError):
        raise ValueError("top_k must be an integer") from None
    return max(1, min(top_k, MAX_TOP_K))


def validate_text_input(text):
    if text is None or not str(text).strip():
        raise ValueError("text is required")
    text = str(text)
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"text exceeds maximum length of {MAX_TEXT_LENGTH}")
    return text
