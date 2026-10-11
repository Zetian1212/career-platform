from app.db import connect_args_for, get_engine


def test_sqlite_gets_check_same_thread():
    assert connect_args_for('sqlite:///./x.db') == {'check_same_thread': False}


def test_postgres_gets_no_sqlite_args():
    assert connect_args_for('postgresql+psycopg://u:p@h/d') == {}


def test_engine_is_reused_for_the_same_url(monkeypatch, tmp_path):
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{tmp_path / "a.db"}')
    assert get_engine() is get_engine()


def test_postgres_url_uses_psycopg_without_connecting(monkeypatch):
    # create_engine is lazy, so nothing is contacted here.
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@127.0.0.1:1/never')
    assert get_engine().dialect.driver == 'psycopg'
