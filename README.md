# Tahoe Golf Scraper — Refactored
A config‑driven, testable, and CI‑ready rewrite of your golf events scraper.

## Highlights
- Config‑driven courses (`courses.json`) so you dont edit Python to add/change courses.
- Robust HTTP with retries, timeouts, and optional caching.
- Centralized logging and error collection.
- Extensible parser registry (add per‑site parsers without touching the core).
- Concurrency to speed up multi‑site scrapes.
- Tests with `pytest` and lint/format checks in GitHub Actions.
- Deterministic JSON output (timestamped + stable sorting).

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py --out out/events.json
```

Add or edit courses in `courses.json`. Each course can reference a `parser` by name.
If you don't have a specific parser yet, try the built‑in `generic_events` which looks
for common event/list markup.

## Developer Notes
- Add a new parser: implement a function in `scraper/parsers.py` with signature
  `(course: dict, html: str, url: str) -> list[dict]` and register it in `PARSERS`.
- Run tests: `pytest -q`
- Format: `black . && isort .`
- Lint: `flake8`
