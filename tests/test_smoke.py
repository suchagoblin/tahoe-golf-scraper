from scraper.parsers import parse_generic_events

def test_generic_parser_smoke():
    html = '''
    <ul class="events">
        <li class="event"><strong>Member-Guest</strong> - Aug 12, 2025</li>
        <li class="event">Club Championship - 09/21/2025</li>
    </ul>
    '''
    events = parse_generic_events({"name": "Demo"}, html, "https://example.com")
    assert len(events) >= 2
    titles = [e["title"] for e in events]
    assert "Member-Guest" in " ".join(titles)
