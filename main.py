import json
from datetime import datetime
from pathlib import Path
import click

from scraper.core import Scraper

@click.command()
@click.option("--config", default="courses.json", help="Path to courses config JSON.")
@click.option("--out", default=None, help="Output JSON path (default: out/events-YYYYMMDD.json).")
@click.option("--concurrency", default=8, show_default=True, help="Max concurrent workers.")
@click.option("--cache/--no-cache", default=True, show_default=True, help="Enable HTTP cache.")
@click.option("--verbose/--quiet", default=True, show_default=True, help="Verbose logging.")
def main(config, out, concurrency, cache, verbose):
    s = Scraper(config_path=config, enable_cache=cache, verbose=verbose, max_workers=concurrency)
    results = s.run()

    Path("out").mkdir(exist_ok=True)
    if out is None:
        out = f"out/events-{datetime.now().strftime('%Y%m%d')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, sort_keys=True)
    click.echo(f"✅ Wrote {len(results.get('events', []))} events to {out}")

if __name__ == "__main__":
    main()
