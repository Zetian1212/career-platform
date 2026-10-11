# career-platform

A FastAPI + Jinja resume and portfolio site for Zetian Tao. Live at **https://zetiantao.me**, running on Railway with PostgreSQL.

## How it runs

```
Browser ──HTTPS──▶ zetiantao.me (Cloudflare DNS, CNAME → xuwtdiji.up.railway.app)
                        │
                        ▼
        Railway project "incredible-truth" (production)
          career-platform service ──private network──▶ Postgres service
          uvicorn, 2 workers, port $PORT                (postgres.railway.internal:5432)
```

- **Deploys:** the `career-platform` service builds from this GitHub repo. It currently deploys the **`railway-postgres`** branch; `main` doesn't have the Postgres changes yet. A push to the deployed branch triggers a new deploy.
- **Build:** Railpack detects Python 3.12 (`.python-version`) and installs `requirements.txt`, so keep `requirements.txt` in step with `pyproject.toml` / `uv.lock`.
- **Deploy settings** live in `railway.json`:
  - pre-deploy: `python -m scripts.init_db` creates any missing tables before the new version starts. It never alters or drops existing ones.
  - start: `uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers`. Railway terminates HTTPS and assigns the port (8080 at the moment).
  - health check: `GET /healthz` must return 200 within 60 s. The service restarts on failure, up to 5 times.
- **Variables** on the `career-platform` service:

  | Variable | Value |
  |---|---|
  | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (private network). A `postgresql://` URL is switched to the psycopg driver automatically. |

  Nothing else is needed. If `DATABASE_URL` is missing, the app quietly falls back to a local SQLite file, which on Railway is empty, so keep it set.
- **Domain:** `zetiantao.me` is a custom domain on the `career-platform` service, with a certificate issued by Railway. DNS is on Cloudflare: the apex is a DNS-only CNAME to `xuwtdiji.up.railway.app`, verified by the `_railway-verify` TXT record. `www.zetiantao.me` still points at the old Azure VM.

Railway warns that `railway.json` (config as code) is deprecated in favour of `.railway/railway.ts`. Existing files keep working until 2026-12-01.

## Checking on it

With the [Railway CLI](https://docs.railway.com/cli) logged in and linked (`railway link --project incredible-truth --environment production --service career-platform`):

```bash
railway deployment list          # recent deploys and their status
railway logs --build <deploy-id> # build log
railway logs --deployment <deploy-id> # runtime log
railway domain list              # domains (a bare `railway domain` CREATES one)
curl https://zetiantao.me/healthz
```

## Editing content

There is no admin area; `/admin` was removed. Content lives in the Railway Postgres, and you edit it there directly:

```bash
railway connect Postgres   # opens psql on the production database
```

For example, the "Chinese" skill was added with:

```sql
INSERT INTO skill (name, category, state, sort_order) VALUES ('Chinese', 'languages', 'published', 9);
```

- Only rows with `state = 'published'` appear on the site.
- Skills are grouped by `category`: `finance` → "Finance", and `tool` / `language` / `library` / `framework` → "Technical". Any other category becomes its own heading, shown as "*Category* skills".
- Changes appear immediately, with no redeploy.

### Fallback snapshot

`app/static/fallback/profile.json` is the cached core profile (name, headline, summary, links, top skills, education) that the site falls back on if the profile can't be read from the database. The `interests` list is edited in this file by hand. After changing the profile in the database, regenerate the file from the production data and commit it:

```bash
DATABASE_URL="$(railway variables --service Postgres --kv | sed -n 's/^DATABASE_PUBLIC_URL=//p')" \
  uv run python -m scripts.generate_snapshot
```

Known limitation: the fallback only covers the profile. If the database is down, `/contact` and `/healthz` still load, but `/`, `/resume` and `/portfolio` currently return 500. If the database is down when the app starts, the app can't start.

## Local development

```bash
uv sync
DATABASE_URL=sqlite:////tmp/career-local.db uv run python -m scripts.seed_demo --reset
DATABASE_URL=sqlite:////tmp/career-local.db uv run uvicorn app.main:create_app --factory --reload --port 8000
```

Then open http://localhost:8000 and check `/healthz`.

- `scripts/seed_demo.py` loads demo content. It only works on SQLite and refuses any other URL, so it can't touch production.
- The local database lives in `/tmp` so it stays out of the repo. Don't point it at `career_platform.db`, which is tracked in git.

## Tests

```bash
uv run pytest -q
```

To also run the Postgres copy test, point `TEST_POSTGRES_URL` at a throwaway database whose name ends in `_test`, for example a local Postgres: `TEST_POSTGRES_URL=postgresql://$USER@localhost/career_test uv run pytest -q`.

## History: moving from the Azure VM

The site used to run on an Azure VM with SQLite, which is still up and still serves `www.zetiantao.me`. On 2026-10-08 its database was copied into the Railway Postgres with:

```bash
TARGET_DATABASE_URL='postgresql://...' uv run python -m scripts.copy_sqlite_to_postgres path/to/career_platform.db
```

The script copies in one transaction, refuses a target that already has rows, and resets the ID sequences. The VM database is no longer kept in sync; Railway is the source of truth. Details are in `docs/superpowers/plans/2026-10-08-railway-postgres-migration.md`.
