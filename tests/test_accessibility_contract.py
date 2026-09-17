def test_public_pages_have_navigation_and_main(client):
    for path in ['/', '/resume', '/portfolio', '/contact']:
        response = client.get(path)
        assert response.status_code == 200
        assert '<main' in response.text
        assert 'Primary navigation' in response.text
