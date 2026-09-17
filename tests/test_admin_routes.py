def test_admin_dashboard_requires_authentication(client):
    response = client.get('/admin', follow_redirects=False)
    assert response.status_code == 303
    assert response.headers['location'] == '/admin/login'


def test_login_page_exists(client):
    response = client.get('/admin/login')
    assert response.status_code == 200
    assert 'Admin login' in response.text
