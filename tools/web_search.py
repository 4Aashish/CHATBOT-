from __future__ import annotations

import urllib.parse
import webbrowser


def search(query: str) -> str:
    """Opens a user-visible search; research summarization needs an AI/web provider."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    return url
