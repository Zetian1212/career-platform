# career-platform

This project is a FastAPI-based resume and portfolio platform for a personal career site.

## Local development

```bash
python -m pip install -r requirements.txt
python scripts/seed_demo.py --reset
python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

## Health

Visit `/healthz` to confirm the application is responding.

## Tests

```bash
pytest -q
```
