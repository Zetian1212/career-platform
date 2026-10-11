import pytest
from scripts.seed_demo import seed_demo


def test_seed_is_repeatable():
    seed_demo(reset=True)
    seed_demo(reset=False)
    assert True


def test_seed_refuses_non_sqlite(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@127.0.0.1:1/never')
    with pytest.raises(SystemExit):
        seed_demo(reset=True)
