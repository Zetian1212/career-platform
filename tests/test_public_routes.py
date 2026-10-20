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


def test_empty_project_table_is_a_healthy_page(client):
    for path in ['/', '/portfolio']:
        response = client.get(path)
        assert response.status_code == 200
        assert 'Projects will appear here as they are published.' in response.text
        assert 'Projects temporarily unavailable.' not in response.text


def test_database_outage_keeps_profile_and_returns_503(tmp_path, monkeypatch):
    import os
    from fastapi.testclient import TestClient
    from app.db import init_db
    from app.main import create_app

    fallback_name = json.loads(Path('app/static/fallback/profile.json').read_text())['profile']['name']
    missing_dir = tmp_path / 'not-yet'
    monkeypatch.setitem(os.environ, 'DATABASE_URL', f'sqlite:///{missing_dir / "down.db"}')
    # The database can't be opened at startup; the app must still start.
    with TestClient(create_app()) as client:
        for path in ['/', '/portfolio', '/portfolio/career-platform']:
            response = client.get(path)
            assert response.status_code == 503, path
            assert 'Projects temporarily unavailable.' in response.text
            assert fallback_name in response.text
        resume = client.get('/resume')
        assert resume.status_code == 503
        assert fallback_name in resume.text
        assert client.get('/healthz').status_code == 200

        # Bring the database back without restarting the app.
        missing_dir.mkdir()
        init_db()
        response = client.get('/')
        assert response.status_code == 200
        assert 'Projects temporarily unavailable.' not in response.text
        assert client.get('/portfolio').status_code == 200
