from __future__ import annotations

import webbrowser


def open_website(url: str) -> bool:
    if not url.startswith(("http://", "https://")):
        raise ValueError("Only http(s) URLs are allowed.")
    return webbrowser.open(url)
