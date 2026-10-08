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

## Deploying to Railway

`railway.json` holds the deploy settings: `python -m scripts.init_db` runs once before each deploy to create the tables, then the app starts with `uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --proxy-headers`, and Railway checks `/healthz`.

Set these variables on the web service:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (a `postgresql://` URL is switched to the psycopg driver automatically) |
| `ADMIN_USERNAME` | admin login name |
| `ADMIN_PASSWORD` | a long random value |
| `SESSION_SECRET` | a long random value (`openssl rand -hex 32`) |

To copy an existing SQLite database into an empty Postgres once (it refuses if the target has rows):

```bash
TARGET_DATABASE_URL='postgresql://...' uv run python -m scripts.copy_sqlite_to_postgres path/to/career_platform.db
```

`scripts/seed_demo.py` only works on SQLite and refuses any other URL.

## Tests

```bash
pytest -q
```

To also run the Postgres copy test, point `TEST_POSTGRES_URL` at a throwaway database whose name ends in `_test`.
