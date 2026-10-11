import pytest


@pytest.mark.parametrize('method, path', [
    ('get', '/admin'),
    ('get', '/admin/login'),
    ('post', '/admin/login'),
    ('get', '/admin/profile'),
    ('post', '/admin/projects/new'),
])
def test_admin_area_is_removed(client, method, path):
    response = getattr(client, method)(path, follow_redirects=False)
    assert response.status_code == 404
