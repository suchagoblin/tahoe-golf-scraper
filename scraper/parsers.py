from __future__ import annotations
from typing import List, Dict
from bs4 import BeautifulSoup
import re

def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def parse_generic_events(course: dict, html: str, url: str) -> List[Dict]:
    """A generic parser that looks for common 'events' structures:
    - lists with dates and titles
    - elements with classes like 'event', 'events', 'list-event', etc.
    This is a best-effort parser; site-specific parsers will be more accurate.
    """
    soup = BeautifulSoup(html, "lxml")

    events: List[Dict] = []

    candidates = []
    candidates += soup.select(".event, .events, .list-event, .event-item, li.event, article.event")
    # tables with dates/titles
    candidates += soup.select("table tr")
    # fallback: any list items that contain a date-like pattern
    candidates += [li for li in soup.select("li") if re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4}|\bjan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec\b)", li.get_text(" ", strip=True), re.I)]

    seen = set()
    for node in candidates:
        text = _clean_text(node.get_text(" ", strip=True))
        if len(text) < 12:
            continue
        # crude date extraction
        m = re.search(r"(\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?)", text, re.I)
        date = m.group(1) if m else None

        # title heuristic: first sentence before a dash or by length split
        title = None
        if " - " in text:
            title = text.split(" - ", 1)[0]
        elif " | " in text:
            title = text.split(" | ", 1)[0]
        else:
            title = " ".join(text.split()[:10])

        title = _clean_text(title or "Event")
        if (title, date) in seen:
            continue
        seen.add((title, date))

        ev = {
            "title": title,
            "date": date,
            "raw": text[:500],
        }
        events.append(ev)

    return events

PARSERS = {
    "generic_events": parse_generic_events,
    # "edgewood": parse_edgewood,   # example: add site-specific functions and register here
}
