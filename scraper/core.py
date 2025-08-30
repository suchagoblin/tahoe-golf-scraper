from __future__ import annotations
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from .http import HttpClient
from .parsers import PARSERS


class Scraper:
    def __init__(
        self,
        config_path: str = "courses.json",
        enable_cache: bool = True,
        verbose: bool = True,
        max_workers: int = 8,
        timeout: int = 15,
    ) -> None:
        self.config_path = Path(config_path)
        self.enable_cache = enable_cache
        self.max_workers = max_workers
        self.client = HttpClient(enable_cache=enable_cache, timeout=timeout)
        self.errors: List[dict] = []
        self.logger = logging.getLogger("tahoe_golf_scraper")
        level = logging.INFO if verbose else logging.WARNING
        logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
        self.courses = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize into list of course dicts
        courses = []
        for name, info in data.items():
            info = dict(info)
            info.setdefault("name", name)
            if "urls" not in info or not info["urls"]:
                self.logger.warning("Course %s has no URLs; skipping", name)
                continue
            info.setdefault("parser", "generic_events")
            courses.append(info)
        return courses

    def _scrape_course(self, course: Dict[str, Any]) -> List[Dict[str, Any]]:
        parser_name = course.get("parser", "generic_events")
        parser = PARSERS.get(parser_name)
        if not parser:
            self.logger.error(
                "Parser not found: %s (course=%s)", parser_name, course.get("name")
            )
            return []

        events: List[Dict[str, Any]] = []
        for url in course["urls"]:
            try:
                html = self.client.get_text(url)
                parsed = parser(course, html, url)
                for ev in parsed:
                    ev.setdefault("course", course.get("name"))
                    ev.setdefault("location", course.get("location"))
                    ev.setdefault("source_url", url)
                events.extend(parsed)
            except Exception as e:
                self.logger.exception(
                    "Error parsing %s (%s): %s", course.get("name"), url, e
                )
                self.errors.append(
                    {
                        "course": course.get("name"),
                        "url": url,
                        "error": str(e),
                    }
                )
        return events

    def run(self) -> Dict[str, Any]:
        all_events: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._scrape_course, c): c for c in self.courses}
            for fut in as_completed(futures):
                course = futures[fut]
                try:
                    events = fut.result()
                    all_events.extend(events)
                except Exception as e:
                    self.logger.exception("Unhandled course error: %s", e)
                    self.errors.append({"course": course.get("name"), "error": str(e)})

        # de-duplicate events by (course, title, date, url)
        seen = set()
        unique = []
        for ev in all_events:
            key = (
                ev.get("course"),
                ev.get("title"),
                ev.get("date"),
                ev.get("source_url"),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(ev)

        return {
            "events": unique,
            "errors": self.errors,
        }
