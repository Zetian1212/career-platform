import os
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / 'test.db'
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ.setdefault('ADMIN_USERNAME', 'admin')
    os.environ.setdefault('ADMIN_PASSWORD', 'change-me')
    os.environ.setdefault('SESSION_SECRET', 'dev-secret')
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
