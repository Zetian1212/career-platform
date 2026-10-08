# Railway + PostgreSQL Migration Plan

**Goal:** Run the career platform on Railway, backed by Railway's PostgreSQL instead of the SQLite file, with the same content the VM serves today. The VM stays up until Railway is verified.

**Source (inspected 2026-10-08):**

| | |
|---|---|
| Live site | VM `vm-career-platform`, `career-platform.service` (uvicorn, 2 workers, `127.0.0.1:8000`) behind nginx on port 80 |
| Live commit | `1fc1fda` (merge of PR #3). Laptop `main` also has `8330957` (docs only, not deployed) |
| Live data | `~/career-platform/career_platform.db` on the VM. It's the **only** real copy; the git-tracked file is empty. Integrity ok. 1 profile, 1 project, 3 experience, 2 education, 5 certifications, 9 skills, 3 links, 0 media, 0 project_skill. Everything is `published`. No string is near its column limit, and the DB columns match the models exactly |
| Stack | FastAPI, SQLAlchemy 2 (`create_all`, no Alembic), Jinja2, Python 3.12 (`.python-version`), uv (`pyproject.toml` + `uv.lock`) |

**Target:** Existing Railway project with a **Postgres** service and a **web** service (names assumed; replace them below if yours differ). Not inspected yet: the Railway CLI isn't installed on the laptop.

**Status:** Section 3 (code) done on branch `railway-postgres`, pushed but not merged (2026-10-08). Nothing on Railway has been created or changed. Next: sections 1–2.

## What has to change, and why

Found by reading the code. Items 1 to 3 would break the app on Postgres. Items 4 to 6 would break it on Railway.

1. **`connect_args={"check_same_thread": False}` is SQLite-only** (`app/db.py:13`, `scripts/seed_demo.py:15`). psycopg rejects it, so every request would fail. Pass it only when the URL starts with `sqlite`.
2. **There's no Postgres driver.** Add `psycopg[binary]` (psycopg 3). Railway gives `postgresql://…`, which SQLAlchemy maps to psycopg2, so the URL must be rewritten to `postgresql+psycopg://…` in `Settings`.
3. **A new engine is created on every request.** `get_db` calls `get_session_local()`, which calls `create_engine()` each time. On SQLite that's cheap. On Postgres, each engine opens its own connection pool, so connections pile up until Postgres refuses new ones. Cache one engine per URL with `functools.lru_cache` on the URL string. That way the tests, which point `DATABASE_URL` at a fresh temp file each time, still get their own engine.
4. **Port and host.** Railway assigns `$PORT` and routes to `0.0.0.0`. The VM's `--host 127.0.0.1 --port 8000` would never receive traffic.
5. **Two workers racing `create_all` on first boot.** `create_app()` calls `init_db()` in every worker. Against an empty Postgres, two workers creating the same tables at once can fail with a duplicate-type error. A Railway **pre-deploy command** that runs `init_db()` once, before the workers start, avoids this. After that, startup `create_all` is a no-op.
6. **HTTPS behind a proxy.** Railway terminates TLS and forwards plain HTTP. Add `--proxy-headers --forwarded-allow-ips='*'` so redirects such as `/admin/login` → `/admin` keep `https`. Optional hardening: set `secure=True` on the two admin cookies, since the site will always be HTTPS.

Things that need **no** change: `app/static/fallback/profile.json` is only read at runtime, so Railway's temporary filesystem is fine. `/healthz` doesn't touch the DB, so it works as the health check. The tests keep using SQLite.

## Steps

Each step lists **Where**, **Run**, **Why**, **Check** and **Undo**.

### 1. Railway access (laptop)

- [ ] **1.1 Install and log in.**
  **Run:** `brew install railway`, then type `! railway login` in Claude Code. The login is interactive, so you run it yourself. Then run `railway link` from the repo and pick the project and the **web** service.
  **Check:** `railway status` shows the project and the web service. `railway variables --service Postgres --kv | cut -d= -f1` lists names such as `DATABASE_URL` and `DATABASE_PUBLIC_URL` without printing values.
  **Undo:** `railway unlink`.
- [ ] **1.2 Record what's already there (read-only).** Find out whether the web service is connected to the GitHub repo and auto-deploys `main`. If it is, **step 3's push deploys immediately**, so step 2's variables must be set first. Also note its current variables and any custom domain.

### 2. Web service variables (Railway)

- [ ] **2.1 Set the variables on the web service:**
  - `DATABASE_URL=${{Postgres.DATABASE_URL}}`. This is a reference variable that goes over the private network (`postgres.railway.internal`), with no egress cost.
  - `ADMIN_USERNAME`, plus new random values for `ADMIN_PASSWORD` and `SESSION_SECRET`. Generate them with `openssl rand -hex 32`. Don't reuse the VM's values.
  - `FALLBACK_PROFILE_PATH` and `APP_NAME` can stay at their defaults.
  **Check:** the names show up in `railway variables --kv | cut -d= -f1`, and no `change-me` defaults are left.
  **Undo:** delete the variables in the Railway dashboard.

### 3. Code changes (laptop, on a branch)

Detailed, test-first steps with the exact code are in **`2026-10-08-railway-postgres-implementation.md`** (Tasks 1–7). The checklist below is the summary.

- [x] **3.1 Make the app Postgres-ready** (items 1 to 3 above): add `psycopg[binary]` with `uv add`, which updates `pyproject.toml` and `uv.lock`. Also add it to `requirements.txt`. Normalize the URL in `app/config.py`. Cache the engine and make `connect_args` conditional in `app/db.py`. Apply the same `connect_args` fix in `scripts/seed_demo.py`.
- [x] **3.2 Add `railway.json`** (config as code, so the deploy settings live in git). It sets the pre-deploy command `python -m scripts.init_db`, a start command on `0.0.0.0:$PORT` with `--proxy-headers`, and the health check `/healthz`. The exact file is in implementation Task 5.
- [x] **3.3 Add `scripts/copy_sqlite_to_postgres.py`.** It reads every table from a SQLite file in `Base.metadata.sorted_tables` order (parents before children), inserts the rows into the target with SQLAlchemy Core, and then resets each `id` sequence with `setval(pg_get_serial_sequence(table, 'id'), max(id))`. Without that last part, the first new project added through `/admin` would fail with a duplicate key. It **refuses to run if the target already has rows**, so it can't be run twice by accident. It prints the row counts per table for both sides.
- [x] **3.4 Tests.** `uv run pytest -q` must pass (still on SQLite). Also start the app once locally against a throwaway Postgres (`docker run postgres:16` or a second Railway database), then check `/`, `/resume`, `/portfolio` and an admin login.
- [x] **3.5 Update the README** with the Railway start command and variables. Keep the `uvicorn` and `/healthz` mentions that `tests/test_deployment_contract.py` checks for.
  **Undo for section 3:** revert the merge commit. The changes keep SQLite working, so the VM is unaffected even if it pulls them.
  **Before committing or pushing:** ask first (see 1.2 about auto-deploy).

### 4. First deploy (Railway)

- [ ] **4.1 Deploy the branch** (merge to `main` if the service tracks `main`, or run `railway up`).
  **Check:** the build log shows Python 3.12 and `psycopg` installed. The pre-deploy log shows `init_db` exiting with code 0. The health check passes. `https://<service>.up.railway.app/healthz` returns `{"status":"ok"}`. `/` shows "Demo Candidate" with the fallback banner, which is **expected**: the tables exist but are still empty.
  **Undo:** roll back to the previous deployment in the dashboard.

### 5. Move the data (laptop → Railway Postgres)

- [ ] **5.1 Freeze edits.** Don't use `/admin` on the VM from here until cutover. Otherwise changes after the copy would be lost.
- [ ] **5.2 Get a consistent copy of the VM DB.**
  **Run:** `ssh … 'sqlite3 ~/career-platform/career_platform.db ".backup /home/azureuser/career_platform.db.for-railway"'`, then `scp` it to `~/Downloads/career_platform.for-railway.db`. Use `.backup` rather than `cp`, because it's safe while uvicorn has the file open.
  **Check:** `pragma integrity_check` returns `ok`, and the row counts match the Source table above.
- [ ] **5.3 Copy.**
  **Run:** `scripts/copy_sqlite_to_postgres.py`, with the SQLite copy and the Postgres **public** URL (`DATABASE_PUBLIC_URL`) as arguments. The private `DATABASE_URL` only resolves inside Railway, so the laptop can't use it. Don't store the public URL in a file.
  **Check:** the row counts per table are identical on both sides. `select max(id)` matches `currval` of each sequence.
  **Undo:** `TRUNCATE profile, link, experience, education, skill, project, project_skill, certification, media_asset RESTART IDENTITY CASCADE;`, then copy again.

### 6. Verify on Railway

- [ ] **6.1** `/`, `/resume`, `/portfolio`, `/portfolio/career-platform`, `/contact` and `/healthz` all return 200. The home page `<h1>` is "Zetian Tao" with **no** fallback banner. The resume shows 3 experience entries, 2 schools and 5 certifications.
- [ ] **6.2** The admin login works over HTTPS and redirects to `https://…/admin`, not `http://`. Adding a test project as a draft succeeds, which proves the sequences were reset. Then delete it, or leave it unpublished.
- [ ] **6.3** Redeploy once (or restart the service) and check 6.1 again. This proves the data lives in Postgres and doesn't depend on the container.

### 7. Cutover and VM retirement (your decision)

- [ ] **7.1** Point visitors at the Railway URL: update links in the README, LinkedIn and anywhere else they appear. Add a custom domain in Railway if you want one.
- [ ] **7.2** Keep the VM running, unchanged, for a few days as a fallback. Then **stop** it (`az vm deallocate`) to stop compute charges. Delete `rg-career-platform` only when you're sure, because that can't be undone, and it also removes the public IP (see the cleanup caveat in the VM notes).
- [ ] **7.3** Optional cleanup: stop tracking `career_platform.db` in git (`git rm --cached` and add it to `.gitignore`). It's an empty, misleading copy once Postgres is the source of truth.

## Risks

- **Auto-deploy before variables are set.** If the web service tracks `main`, pushing step 3 without step 2 would boot the app with the default SQLite URL and default admin password. Do step 2 first.
- **Public DB URL.** It's needed only for step 5.3. Don't paste it into files or commits. If it leaks, regenerate the Postgres password in Railway.
- **Data drift.** Any admin edit on the VM after 5.2 isn't copied. That's why step 5.1 exists.

## Progress log

- **2026-10-08:** Inspected the code and the live VM DB (read-only). The live site is on `1fc1fda`. Wrote this plan.
- **2026-10-08:** Wrote the implementation plan for section 3 (`2026-10-08-railway-postgres-implementation.md`). Changes from the summary above: the pre-deploy command is now `python -m scripts.init_db`, and the start command is wrapped in `sh -c`, both to avoid quoting problems. `scripts/seed_demo.py` gets a guard so `--reset` can never drop a Postgres database. Found while writing it: the laptop has no Docker or Postgres, so Task 4 installs `postgresql@16` with Homebrew for local tests.
- **2026-10-08 (21:47 UTC):** Backed up the live VM DB with `sqlite3 .backup` (safe while uvicorn runs) to `~/career_platform.db.backup-20261008T214759Z` on the VM, outside the repo folder, 49152 bytes, SHA-256 `42f9e678…c134633b`. Checked: `integrity_check` ok; per-table row counts match the live DB; the profile, project and 3 experience rows read back correctly; the full `.dump` of the backup is identical to the live DB's. This is a safety copy only. Step 5.2 still takes its own fresh copy after edits are frozen.
- **2026-10-08:** Section 3 done (see the implementation plan's log). The real data was rehearsed on a local Postgres 16, not Railway. Branch `railway-postgres` was pushed and **not merged**. Merge only after 2.1, in case the web service auto-deploys `main`.
