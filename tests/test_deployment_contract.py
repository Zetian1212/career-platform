import json
from pathlib import Path

def test_production_start_command_is_documented():
    readme = Path('README.md').read_text()
    assert 'uvicorn' in readme.lower()
    assert '/healthz' in readme


def test_railway_config_listens_on_railway_port():
    deploy = json.loads(Path('railway.json').read_text())['deploy']
    assert deploy['healthcheckPath'] == '/healthz'
    assert deploy['preDeployCommand'] == 'python -m scripts.init_db'
    start = deploy['startCommand']
    assert '--host 0.0.0.0' in start and '$PORT' in start.replace('${PORT:-8000}', '$PORT')
    assert '--proxy-headers' in start
