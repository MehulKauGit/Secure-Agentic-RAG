"""Mock / deterministic web search tool for reproducible agent evaluations."""

MOCK_SEARCH_DATABASE: dict[str, str] = {
    "weather": "Current forecast: Sunny, 72°F (22°C), humidity 45%, wind 5 mph NW.",
    "revenue 2024": "Global Corp Annual Financial Report 2024: Total Revenue $4.8B (+14% YoY), Net Income $620M.",
    "ai security": "OWASP Top 10 for Large Language Model Applications highlights Prompt Injection as the #1 threat.",
    "quarterly meeting": "The Q3 All-Hands meeting is scheduled for Thursday, September 18 at 10:00 AM EST.",
}


def web_search_stub(query: str) -> str:
    """Searches a mock corporate/public web repository for query terms."""
    q = query.lower().strip()
    for key, result in MOCK_SEARCH_DATABASE.items():
        if key in q or any(word in q for word in key.split()):
            return f"[Search Result for '{query}']:\n{result}"
    return f"[Search Result for '{query}']:\nNo matching external articles found for the given search query."
