def test_health_endpoint_returns_ok(client):
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_homepage_renders_shell(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Career Platform' in response.text
    assert 'Demo Candidate' in response.text
