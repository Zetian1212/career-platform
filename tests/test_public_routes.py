import json
from pathlib import Path


def test_health_endpoint_returns_ok(client):
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_homepage_renders_shell(client):
    fallback_name = json.loads(Path('app/static/fallback/profile.json').read_text())['profile']['name']
    response = client.get('/')
    assert response.status_code == 200
    assert 'Career Platform' in response.text
    assert fallback_name in response.text


def test_analytics_loads_once_behind_consent(client):
    for path in ['/', '/privacy', '/no-such-page']:
        html = client.get(path).text
        assert html.count('/static/js/analytics.js') == 1
        assert 'data-ga-id="G-3XLF72EHQC"' in html
        assert 'googletagmanager.com' not in html
        assert 'id="consent-banner"' in html


def test_analytics_script_defaults_to_denied():
    script = Path('app/static/js/analytics.js').read_text()
    assert "analytics_storage: 'denied'" in script
    assert script.index("gtag('consent', 'default'") < script.index('googletagmanager.com')
