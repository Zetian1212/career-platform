from pathlib import Path

def test_production_start_command_is_documented():
    readme = Path('README.md').read_text()
    assert 'uvicorn' in readme.lower()
    assert '/healthz' in readme
