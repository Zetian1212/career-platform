# Railway + PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the career platform run on Railway against Railway's PostgreSQL, keep it working on SQLite (for the VM and the tests), and provide a safe one-off script that copies the live SQLite content into Postgres.

**Architecture:** No new layers. `app/config.py` normalizes whatever database URL it's given to a SQLAlchemy URL with an explicit driver. `app/db.py` builds **one** engine per URL and reuses it, passing SQLite-only options only to SQLite. Schema creation stays `Base.metadata.create_all`, but on Railway it runs once in a pre-deploy command so the two uvicorn workers don't race each other. Data moves with a small SQLAlchemy Core script that copies tables in dependency order and then resets Postgres ID sequences.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, psycopg 3 (`psycopg[binary]`), uv, pytest, Railway (Railpack builder, `railway.json` config as code).

**Runbook:** `docs/superpowers/plans/2026-10-08-railway-postgres-migration.md` covers the operational side (Railway variables, deploy, data copy, verification, cutover). This plan is that runbook's **section 3**. Finish it before runbook section 4.

## Global Constraints

- SQLite must keep working unchanged. The VM keeps serving from SQLite until cutover, and the tests stay on SQLite.
- No Alembic and no schema changes. The models already match the live DB exactly (checked 2026-10-08).
- Nothing in the code or tests may read or write the production Postgres. Only the copy script touches it, and only when run by hand with an explicit URL.
- No secrets in files or commits. Database URLs reach the code only through environment variables.
- Work on a branch (`railway-postgres`). Ask before every commit and push. If the Railway web service auto-deploys `main`, its variables must be set (runbook 2.1) before merging.

## File and module map

- `pyproject.toml`, `uv.lock`, `requirements.txt`: add `psycopg[binary]`.
- `app/config.py`: add `normalize_database_url()` and a validator on `Settings.database_url`.
- `app/db.py`: add `connect_args_for()`, a cached `_engine_for()`, and `pool_pre_ping`.
- `scripts/init_db.py` (new): `python -m scripts.init_db` creates the tables. This is Railway's pre-deploy command.
- `scripts/seed_demo.py`: refuse non-SQLite URLs. Its `--reset` runs `drop_all`.
- `scripts/copy_sqlite_to_postgres.py` (new): the one-off data copy.
- `railway.json` (new): build and deploy settings.
- `tests/test_config.py` (new), `tests/test_db.py` (new), `tests/test_copy_script.py` (new), `tests/test_seed_workflow.py`, `tests/test_deployment_contract.py`.
- `README.md`, `.env.example`: Railway docs.

---

## Task 1: Postgres driver and URL normalization

**Files:**
- Modify: `pyproject.toml`, `uv.lock`, `requirements.txt`, `app/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- `normalize_database_url(url: str) -> str` in `app/config.py`
- `Settings.database_url` is always normalized.

- [x] **Step 1: Write the failing tests**

```python
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
```

- [x] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_config.py -q`
Expected: FAIL with `ImportError: cannot import name 'normalize_database_url'`.

- [x] **Step 3: Add the driver**

Run: `uv add 'psycopg[binary]>=3.2'`. Then add the line `psycopg[binary]>=3.2` to `requirements.txt`.
Check: `uv run python -c "import psycopg; print(psycopg.__version__)"` prints a 3.x version.

- [x] **Step 4: Implement**

In `app/config.py`:

```python
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_POSTGRES_PREFIXES = ('postgres://', 'postgresql://')


def normalize_database_url(url: str) -> str:
    """Pin Postgres URLs to psycopg 3; Railway hands out plain postgresql:// URLs."""
    for prefix in _POSTGRES_PREFIXES:
        if url.startswith(prefix):
            return 'postgresql+psycopg://' + url[len(prefix):]
    return url
```

Inside `Settings`:

```python
    @field_validator('database_url')
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        return normalize_database_url(value)
```

- [x] **Step 5: Run the tests**

Run: `uv run pytest -q`
Expected: all pass (the existing 10 plus the new ones).

**Done looks like:** any Postgres URL Railway gives the app resolves to the psycopg 3 driver, and SQLite URLs are untouched.

---

## Task 2: One engine per URL, SQLite-only connect args

**Files:**
- Modify: `app/db.py`
- Create: `tests/test_db.py`

**Interfaces:**
- `connect_args_for(url: str) -> dict` in `app/db.py`
- `get_engine()` returns the **same** `Engine` for the same URL. `get_session_local()` and `init_db()` keep their signatures.

- [x] **Step 1: Write the failing tests**

```python
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
```

- [x] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_db.py -q`
Expected: FAIL with `ImportError: cannot import name 'connect_args_for'`.

- [x] **Step 3: Implement**

Replace `get_engine` in `app/db.py`:

```python
from functools import lru_cache


def connect_args_for(url: str) -> dict:
    # check_same_thread is a sqlite3 option; psycopg rejects unknown arguments.
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


@lru_cache(maxsize=None)
def _engine_for(url: str):
    return create_engine(url, connect_args=connect_args_for(url), pool_pre_ping=True)


def get_engine():
    return _engine_for(get_settings().database_url)
```

The cache is keyed on the URL, not global. Tests that point `DATABASE_URL` at a fresh temp file each time still get a fresh engine. `pool_pre_ping` replaces connections that Postgres closed while idle.

- [x] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass.

**Done looks like:** a request on Postgres borrows a connection from one long-lived pool instead of opening a new pool per request.

---

## Task 3: Schema bootstrap command and a guard on the demo seeder

**Files:**
- Create: `scripts/init_db.py`
- Modify: `scripts/seed_demo.py`, `tests/test_seed_workflow.py`

**Interfaces:**
- `python -m scripts.init_db` exits 0 after `create_all`.
- `seed_demo()` raises `SystemExit` for any non-SQLite URL, before it connects.

- [x] **Step 1: Write the failing test** (append to `tests/test_seed_workflow.py`)

```python
import pytest


def test_seed_refuses_non_sqlite(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@127.0.0.1:1/never')
    with pytest.raises(SystemExit):
        seed_demo(reset=True)
```

Why: `seed_demo(reset=True)` runs `drop_all`. If `DATABASE_URL` in someone's shell (for example under `railway run`) pointed at production, running the tests would wipe it.

- [x] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_seed_workflow.py -q`
Expected: FAIL. Without the guard, the old path logic runs `mkdir` on the URL and then tries to connect. Afterwards, delete the junk directory it leaves in the repo: `rm -rf 'postgresql+psycopg:'`.

- [x] **Step 3: Implement**

At the top of `seed_demo()`, after `settings = get_settings()`:

```python
    if not settings.database_url.startswith('sqlite'):
        raise SystemExit('seed_demo only writes to local SQLite files; refusing to touch ' + settings.database_url.split('@')[-1])
```

The message prints only the host and database part, never the password. Also switch its `create_engine(...)` call to `create_engine(settings.database_url, connect_args=connect_args_for(settings.database_url))`.

Create `scripts/init_db.py`:

```python
from app.db import init_db

if __name__ == '__main__':
    init_db()
    print('Tables ready.')
```

- [x] **Step 4: Run the tests**

Run: `uv run pytest -q`, then `uv run python -m scripts.init_db`.
Expected: all pass, and the command prints `Tables ready.` against the local SQLite file.

---

## Task 4: SQLite → Postgres copy script

**Files:**
- Create: `scripts/copy_sqlite_to_postgres.py`, `tests/test_copy_script.py`

**Interfaces:**
- `copy_database(source_url: str, target_url: str) -> dict[str, int]` returns the row count copied per table, and raises `SystemExit` if the target has any rows.
- CLI: `TARGET_DATABASE_URL=… uv run python -m scripts.copy_sqlite_to_postgres <source.db>`. The URL comes from the environment, so it never appears in shell history or arguments.

- [x] **Step 1: Write the failing tests** (they use SQLite as the target, so they run anywhere)

```python
import os
from datetime import date
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from app.db import Base
from app.models import Experience, Profile, Project, Skill
from scripts.copy_sqlite_to_postgres import copy_database


def _source(tmp_path):
    url = f'sqlite:///{tmp_path / "source.db"}'
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        profile = Profile(name='Zetian Tao', headline='h', summary='s')
        s.add(profile)
        s.flush()
        s.add(Experience(role='Intern', company='Co', start_date=date(2025, 7, 1), profile_id=profile.id))
        skill = Skill(name='Python')
        project = Project(title='Career Platform', slug='career-platform', summary='s', featured=True)
        project.skills.append(skill)
        s.add_all([skill, project])
        s.commit()
    return url


def test_copy_preserves_rows_types_and_links(tmp_path):
    target = f'sqlite:///{tmp_path / "target.db"}'
    counts = copy_database(_source(tmp_path), target)
    assert counts['profile'] == 1 and counts['project_skill'] == 1
    with Session(create_engine(target)) as s:
        assert s.scalar(select(Experience.start_date)) == date(2025, 7, 1)
        assert s.scalar(select(Project.featured)) is True
        assert s.get(Project, 1).skills[0].name == 'Python'


def test_copy_refuses_non_empty_target(tmp_path):
    source = _source(tmp_path)
    target = f'sqlite:///{tmp_path / "target.db"}'
    copy_database(source, target)
    with pytest.raises(SystemExit):
        copy_database(source, target)


@pytest.mark.skipif('TEST_POSTGRES_URL' not in os.environ, reason='needs a throwaway Postgres')
def test_copy_into_postgres_then_insert(tmp_path):
    url = os.environ['TEST_POSTGRES_URL']
    assert url.rsplit('/', 1)[-1].endswith('_test'), 'refusing: database name must end in _test'
    engine = create_engine(url.replace('postgresql://', 'postgresql+psycopg://', 1))
    Base.metadata.drop_all(engine)
    try:
        copy_database(_source(tmp_path), url)
        with Session(engine) as s:
            # Fails with a duplicate key unless the id sequences were reset.
            s.add(Project(title='New', slug='new', summary='s'))
            s.commit()
            assert s.scalar(select(func.max(Project.id))) == 2
    finally:
        Base.metadata.drop_all(engine)
```

- [x] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_copy_script.py -q`
Expected: FAIL with `ModuleNotFoundError: scripts.copy_sqlite_to_postgres`. The Postgres test is skipped.

- [x] **Step 3: Implement** `scripts/copy_sqlite_to_postgres.py`

```python
"""Copy every row from a SQLite career-platform database into an empty target database.

Usage: TARGET_DATABASE_URL=postgresql://... uv run python -m scripts.copy_sqlite_to_postgres path/to/source.db
"""
from __future__ import annotations
import os
import sys
from sqlalchemy import create_engine, func, select, text
from app.config import normalize_database_url
from app.db import Base, connect_args_for
import app.models  # noqa: F401  (registers the tables on Base.metadata)


def _count(conn, table) -> int:
    return conn.execute(select(func.count()).select_from(table)).scalar_one()


def copy_database(source_url: str, target_url: str) -> dict[str, int]:
    target_url = normalize_database_url(target_url)
    source = create_engine(source_url, connect_args=connect_args_for(source_url))
    target = create_engine(target_url, connect_args=connect_args_for(target_url))
    Base.metadata.create_all(bind=target)
    tables = Base.metadata.sorted_tables  # parents before children
    counts: dict[str, int] = {}
    with source.connect() as src, target.begin() as dst:
        occupied = [t.name for t in tables if _count(dst, t)]
        if occupied:
            raise SystemExit(f"Target already has rows in: {', '.join(occupied)}. Nothing copied.")
        for table in tables:
            rows = [dict(row._mapping) for row in src.execute(select(table))]
            if rows:
                dst.execute(table.insert(), rows)
            counts[table.name] = len(rows)
        if dst.dialect.name == 'postgresql':
            # Rows arrived with explicit ids, so move each sequence past the highest one.
            for table in tables:
                if 'id' in table.c:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table.name}"
                    ))
    with target.connect() as dst:
        mismatched = {t.name for t in tables if _count(dst, t) != counts[t.name]}
    if mismatched:
        raise SystemExit(f"Row counts differ after copy: {sorted(mismatched)}")
    return counts


if __name__ == '__main__':
    if len(sys.argv) != 2 or 'TARGET_DATABASE_URL' not in os.environ:
        raise SystemExit(__doc__)
    for name, n in copy_database(f'sqlite:///{sys.argv[1]}', os.environ['TARGET_DATABASE_URL']).items():
        print(f'{name}: {n}')
```

The table names come from our own models, not from user input, so the f-string SQL is safe.

- [x] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass, with 1 skipped (the Postgres test).

- [x] **Step 5: Run the Postgres test locally**

There's no Docker or Postgres on the laptop yet. Install a throwaway one:
`brew install postgresql@16 && brew services start postgresql@16 && /opt/homebrew/opt/postgresql@16/bin/createdb career_test`
Run: `TEST_POSTGRES_URL=postgresql://$USER@localhost/career_test uv run pytest tests/test_copy_script.py -q`
Expected: 3 passed.

**Done looks like:** the live 24 rows can be copied in one transaction (all or nothing), the script refuses to run twice, and new rows added through `/admin` afterwards get fresh IDs.

---

## Task 5: Railway configuration as code

**Files:**
- Create: `railway.json`
- Modify: `tests/test_deployment_contract.py`

- [x] **Step 1: Write the failing test** (append)

```python
import json


def test_railway_config_listens_on_railway_port():
    deploy = json.loads(Path('railway.json').read_text())['deploy']
    assert deploy['healthcheckPath'] == '/healthz'
    assert deploy['preDeployCommand'] == 'python -m scripts.init_db'
    start = deploy['startCommand']
    assert '--host 0.0.0.0' in start and '$PORT' in start.replace('${PORT:-8000}', '$PORT')
    assert '--proxy-headers' in start
```

- [x] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_deployment_contract.py -q`
Expected: FAIL with `FileNotFoundError: railway.json`.

- [x] **Step 3: Create `railway.json`**

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "preDeployCommand": "python -m scripts.init_db",
    "startCommand": "sh -c 'uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --proxy-headers --forwarded-allow-ips=\"*\"'",
    "healthcheckPath": "/healthz",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

Why `sh -c`: it guarantees `$PORT` is expanded whether or not Railway runs the command through a shell. The quotes around `*` stop the shell from turning it into a list of filenames. Railpack detects `uv.lock` and `.python-version` (3.12) on its own.

- [x] **Step 4: Check the command locally**

Run: `PORT=8123 sh -c 'uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --proxy-headers --forwarded-allow-ips="*"'`, then `curl -s localhost:8123/healthz` and Ctrl-C.
Expected: `{"status":"ok"}`, and the log says `Uvicorn running on http://0.0.0.0:8123`.

- [x] **Step 5: Run the tests**

Run: `uv run pytest -q`
Expected: all pass, with 1 skipped.

---

## Task 6: Documentation

**Files:**
- Modify: `README.md`, `.env.example`

- [x] **Step 1:** In `.env.example`, add a comment above `DATABASE_URL`: `# Local: SQLite file. Railway: set to ${{Postgres.DATABASE_URL}} on the web service.`
- [x] **Step 2:** Add a "Deploying to Railway" section to `README.md`. Cover: the variables (`DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SESSION_SECRET`); that `railway.json` holds the start, pre-deploy and health-check settings; and the one-off copy command from Task 4. Keep the existing `uvicorn` and `/healthz` mentions, which `test_production_start_command_is_documented` checks for.
- [x] **Step 3:** Run `uv run pytest -q`. Expected: all pass.

---

## Task 7: Full verification against a real Postgres, then hand off

- [x] **Step 1:** Run `uv run pytest -q`. Expected: all pass, with 1 skipped.
- [x] **Step 2:** Run `TEST_POSTGRES_URL=postgresql://$USER@localhost/career_test uv run pytest -q`. Expected: all pass, with 0 skipped.
- [x] **Step 3: Rehearse the whole migration locally.**
  - Get a copy of the live DB (runbook 5.2), then run `/opt/homebrew/opt/postgresql@16/bin/createdb career_rehearsal`.
  - Run `TARGET_DATABASE_URL=postgresql://$USER@localhost/career_rehearsal uv run python -m scripts.copy_sqlite_to_postgres ~/Downloads/career_platform.for-railway.db`.
  - Start the app with `DATABASE_URL=postgresql://$USER@localhost/career_rehearsal PORT=8123 sh -c '…'` (the Task 5 command).
  **Expected:** counts printed as profile 1, project 1, experience 3, education 2, certification 5, skill 9, link 3, and 0 for the rest. On `localhost:8123`, `/` shows "Zetian Tao" with no fallback banner. `/resume` shows 3 jobs, 2 schools and 5 certifications. Logging in to `/admin` and adding a draft project succeeds. A second run of the copy command refuses.
- [x] **Step 4:** Show the diff, then **ask before committing and pushing** the `railway-postgres` branch. Merge only once runbook 2.1 (Railway variables) is done.
- [ ] **Step 5:** Continue with runbook section 4 (first deploy).

---

## Not in this plan

- Alembic migrations. `create_all` is enough while the schema doesn't change. Add Alembic before the first change to a column.
- `secure=True` on the admin cookies, rate-limiting logins, and moving the CSS hashing off import time. These are worth doing, but they're separate changes.
- Untracking `career_platform.db` from git (runbook 7.3).

## Plan self-review

### Coverage of the runbook's "what has to change"

- 1 (SQLite-only connect args): Task 2, plus Task 3 for the seeder.
- 2 (driver and URL): Task 1.
- 3 (engine per request): Task 2.
- 4 (port and host): Task 5.
- 5 (two workers racing `create_all`): Task 3 (`scripts/init_db.py`) and Task 5 (`preDeployCommand`).
- 6 (HTTPS behind a proxy): Task 5 (`--proxy-headers`).
- Data move and ID sequences: Task 4, rehearsed in Task 7.

### Placeholder scan

No TBDs. Values that only exist at deploy time (Railway URLs and secrets) are supplied through environment variables and are covered in runbook 1.1 and 2.1.

### Interface consistency

`normalize_database_url` (Task 1) is used by `Settings` and by the copy script. `connect_args_for` (Task 2) is used by `app/db.py`, `scripts/seed_demo.py` and the copy script. `init_db()` keeps its signature and is called from `create_app()` and `scripts/init_db.py`.

## Progress log

- **2026-10-08:** Plan written. Nothing implemented yet.
- **2026-10-08:** Tasks 1–6 done on branch `railway-postgres`. Each new test failed first for the expected reason, then passed. psycopg 3.3.6 was added. Running Task 3's failing test did create the junk `postgresql+psycopg:/` folder, and it was deleted. Installed `postgresql@16` with Homebrew (it now runs as a background service on the laptop) and created the `career_test` and `career_rehearsal` databases. Suite: 23 passed and 1 skipped on SQLite; 24 passed with `TEST_POSTGRES_URL`.
- **2026-10-08:** Task 5 step 4: the exact `railway.json` start command ran with `PORT=8123` (under `uv run`, so the venv was on the PATH). It logged `Uvicorn running on http://0.0.0.0:8123`, and `/healthz` returned ok.
- **2026-10-08:** Task 7 rehearsal on real data. Copied the VM backup `career_platform.db.backup-20261008T214759Z` (SHA-256 matches) to `~/Downloads`, then into the local `career_rehearsal` database. Counts: profile 1, project 1, skill 9, certification 5, education 2, experience 3, link 3, media 0, project_skill 0. A second run refused ("Target already has rows"). Then ran the app on that Postgres using the `railway.json` command. All six public paths returned 200. The `<h1>` is "Hi, I'm Zetian." with no fallback banner, and the resume lists all 3 internships and LMU. Admin login returned 303 with a **relative** `Location: /admin`, so it stays on https behind Railway's proxy. Adding a draft project got id 2, so the sequence reset works. No errors in the log. Not related to the migration, but the home page text still says "Self-hosted on an Azure Ubuntu VM … backed by SQLite", which will be out of date on Railway. That's a content edit, left for you.
- **2026-10-08:** Step 4: you asked for commit and push. The branch is pushed, **not merged to `main`**, so nothing auto-deploys before the Railway variables (runbook 2.1) are set. Nothing was created or changed on Railway.
