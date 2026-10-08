import pytest
from app.config import Settings, normalize_database_url


@pytest.mark.parametrize('given, expected', [
    ('postgresql://u:p@db.internal:5432/railway', 'postgresql+psycopg://u:p@db.internal:5432/railway'),
    ('postgres://u:p@db.internal:5432/railway', 'postgresql+psycopg://u:p@db.internal:5432/railway'),
    ('postgresql+psycopg://u:p@h/d', 'postgresql+psycopg://u:p@h/d'),
    ('sqlite:///./career_platform.db', 'sqlite:///./career_platform.db'),
])
def test_normalize_database_url(given, expected):
    assert normalize_database_url(given) == expected


def test_settings_normalizes_database_url(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@h:5432/d')
    assert Settings().database_url == 'postgresql+psycopg://u:p@h:5432/d'
