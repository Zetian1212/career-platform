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
