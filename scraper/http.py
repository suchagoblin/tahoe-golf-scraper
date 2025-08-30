from __future__ import annotations
import logging
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import requests_cache
except Exception:
    requests_cache = None  # optional


class HttpClient:
    def __init__(self, enable_cache: bool = True, timeout: int = 15) -> None:
        self.logger = logging.getLogger("tahoe_golf_scraper.http")
        self.timeout = timeout
        self.session = self._build_session(enable_cache)

    def _build_session(self, enable_cache: bool) -> requests.Session:
        if enable_cache and requests_cache is not None:
            session = requests_cache.CachedSession(
                "http_cache",
                expire_after=3600,  # 1 hour
                allowable_methods=("GET",),
            )
        else:
            session = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(
            {"User-Agent": "tahoe-golf-scraper/1.0 (+https://example.com)"}
        )
        return session

    def get_text(self, url: str, *, timeout: Optional[int] = None) -> str:
        t = timeout or self.timeout
        resp = self.session.get(url, timeout=t)
        resp.raise_for_status()
        # Attempt to honor encoding, fallback to apparent encoding
        resp.encoding = resp.encoding or resp.apparent_encoding
        return resp.text
