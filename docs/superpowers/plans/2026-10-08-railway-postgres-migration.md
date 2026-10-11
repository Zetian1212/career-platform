# Railway + PostgreSQL Migration Plan

**Goal:** Run the career platform on Railway, backed by Railway's PostgreSQL instead of the SQLite file, with the same content the VM serves today. The VM stays up until Railway is verified.

**Source (inspected 2026-10-08):**

| | |
|---|---|
| Live site | VM `vm-career-platform`, `career-platform.service` (uvicorn, 2 workers, `127.0.0.1:8000`) behind nginx on port 80 |
| Live commit | `1fc1fda` (merge of PR #3). Laptop `main` also has `8330957` (docs only, not deployed) |
| Live data | `~/career-platform/career_platform.db` on the VM. It's the **only** real copy; the git-tracked file is empty. Integrity ok. 1 profile, 1 project, 3 experience, 2 education, 5 certifications, 9 skills, 3 links, 0 media, 0 project_skill. Everything is `published`. No string is near its column limit, and the DB columns match the models exactly |
| Stack | FastAPI, SQLAlchemy 2 (`create_all`, no Alembic), Jinja2, Python 3.12 (`.python-version`), uv (`pyproject.toml` + `uv.lock`) |

**Target:** Railway project `incredible-truth`, environment `production`. Services: `Postgres` (image `postgres-ssl:18`, PostgreSQL 18.6, public proxy `altaria.proxy.rlwy.net`) and `career-platform` (web; source is the GitHub repo `Zetian1212/career-platform`; its latest deploy had **FAILED** when inspected). Wherever this plan says **web**, it means `career-platform`.

**Status:** Live on Railway at https://zetiantao.me (2026-10-10). The code, admin removal, README and this plan are merged to `main`. Railway's web service still deploys from the `railway-postgres` branch. The admin editor was removed, so section 2.1's `ADMIN_*`/`SESSION_SECRET` no longer apply. Open: point `www` and the Railway branch at the right targets, the DB-down 500s, and retiring the VM (section 7).

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

- [x] **1.1 Install and log in.**
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
- [x] **5.2 Get a consistent copy of the VM DB.**
  **Run:** `ssh … 'sqlite3 ~/career-platform/career_platform.db ".backup /home/azureuser/career_platform.db.for-railway"'`, then `scp` it to `~/Downloads/career_platform.for-railway.db`. Use `.backup` rather than `cp`, because it's safe while uvicorn has the file open.
  **Check:** `pragma integrity_check` returns `ok`, and the row counts match the Source table above.
- [x] **5.3 Copy.**
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
- **2026-10-08:** Installed the Railway CLI 5.64.1 (Homebrew) and logged in with `railway login --browserless` (you approved the device code), as Zetian Tao. Linked the repo to `incredible-truth` / `production`; this only writes local CLI config. Read-only findings: (a) the web service `career-platform` **already has `DATABASE_URL`** pointing at `postgres.railway.internal:5432` (the private URL, as planned). (b) It has **no `ADMIN_USERNAME`, `ADMIN_PASSWORD` or `SESSION_SECRET`**, so a successful deploy would run with the code defaults `admin` / `change-me`, and step 2.1 must be done before any deploy that succeeds. (c) Its latest deploy is FAILED; not investigated yet, but it's probably `main`, which has no psycopg. (d) The CLI warns that `railway.json` (config as code) is deprecated in favour of `.railway/railway.ts`. Existing files keep working until **2026-12-01**.
- **2026-10-08:** Steps 5.2–5.3: you asked for the transfer. The Railway Postgres had **no tables**, so it was empty. Ran `scripts/copy_sqlite_to_postgres.py` on the VM backup `career_platform.db.backup-20261008T214759Z` (SHA-256 `42f9e678…`), using the Postgres `DATABASE_PUBLIC_URL`. The URL was read straight from `railway variables` into the environment and never printed or saved. It ran in one transaction, with exit code 0. Copied: profile 1, project 1, skill 9, certification 5, education 2, experience 3, link 3, media_asset 0, project_skill 0.
- **2026-10-08:** Compared Railway with a **fresh** `.backup` snapshot of the live VM DB. Its SHA-256 `42f9e678…` is the same as the backup, so nothing changed on the VM in between. Every table's row count matches, and every row is identical across all columns (rows ordered by primary key; dates and timestamps put in UTC ISO format on both sides). All 8 id sequences on Railway are past `max(id)`. Result: **MATCH**. The temporary snapshot on the VM (`/tmp/cp-live-compare.db`) and the laptop temp files were deleted. Edit freeze (5.1) applies from now: changes made through `/admin` on the VM won't reach Railway.
- **2026-10-10:** Checked four requirements against branch `railway-postgres`.
  - (1) **URL from an env var: PASS, with a caveat.** No database URL is hard-coded in `app/` or `scripts/`; `DATABASE_URL` drives the engine. If it's unset, the code silently falls back to `sqlite:///./career_platform.db`. On Railway that would be an empty file inside the container, not an error. The web service has only `DATABASE_URL`, pointing at the private `postgres.railway.internal:5432`.
  - (2) **Binds 0.0.0.0 and $PORT: PASS.** The `railway.json` command with `PORT=8765` listened on `*:8765` ("Uvicorn running on http://0.0.0.0:8765").
  - (3) **Pages load with the DB down: FAIL.** On local Postgres, with the DB stopped mid-run using `pg_ctl stop -m fast`, `/`, `/resume`, `/portfolio` and `/portfolio/career-platform` returned **500** (`psycopg.OperationalError`). `/contact`, `/healthz` and `/admin/login` returned 200. The snapshot fallback only covers the profile query; the routes then call `repo.list_projects/list_skills/list_experience/list_certifications/get_project` without a fallback (`app/routes/public.py:46-80`). This code is unchanged from `main`, so it isn't a regression. With the DB down at **startup**, `init_db()` in `create_app()` kills every worker, so nothing is served and the pre-deploy step fails too. Note: a first attempt used `brew services stop`, a smart shutdown that waits for open connections, so the app kept getting answers; that result was thrown away.
  - (4) **No invented sample data: PASS.** Railway's tables are identical to the VM's (2026-10-08 comparison). No demo or rehearsal rows are on Railway. No demo strings are in `app/`. `profile.json` holds only real profile data. Demo content exists only in `scripts/seed_demo.py`, which refuses non-SQLite URLs, and in the tests' temporary databases.
  - Also seen: at 17:07 PDT a Railway build of `main` (`8330957`) started that I didn't trigger. The web service now has the custom domain `zetiantao.me`. It still has no `ADMIN_*` or `SESSION_SECRET` variables.
- **2026-10-10:** You asked to run the migrations against `RAILWAY_DATABASE_URL`. That variable isn't set in my shell, so I set it for the one command from the Railway Postgres `DATABASE_PUBLIC_URL` (`altaria.proxy.rlwy.net`; the value was never printed or saved). The app has no migration tool, so the "migration" is `python -m scripts.init_db` (`create_all`, which only creates missing tables). It printed "Tables ready." and exited 0. All 9 tables already existed from the data copy, so it was a no-op: the column counts per table were the same before and after, the schema matches the models exactly, and the row counts are unchanged (profile 1, project 1, skill 9, certification 5, education 2, experience 3, link 3, media_asset 0, project_skill 0).
- **2026-10-10:** You asked again for the transfer and comparison. I didn't copy again: Railway already had the 2026-10-08 copy, and the script refuses a target with rows. Re-compared against a fresh `.backup` snapshot of the live VM DB. Its SHA-256 `42f9e678…` is still identical to the backup, so the VM hasn't changed since. All 9 tables have equal row counts and identical rows across all columns, and all 8 id sequences are past `max(id)`. Result: **MATCH**. The temporary snapshot files on the VM and laptop were deleted.
- **2026-10-10:** Cloudflare: you installed `cf` 1.0.0-beta.14 (npm) and ran `cf auth login`, as zetian1212@gmail.com; the OAuth token expires the same day, 18:27 PDT. Zone `zetiantao.me` is active and has 9 records (read-only listing). The apex `zetiantao.me` is a CNAME to `xuwtdiji.up.railway.app` (DNS only), with a `_railway-verify` TXT. **`www.zetiantao.me` is an A record to `172.183.16.158`, the Azure VM**, so the apex goes to Railway while `www` still goes to the VM. The rest is Namecheap email forwarding (5 MX records + SPF TXT). Nothing was changed.
- **2026-10-10:** Railway CLI check: it was still logged in (Zetian Tao), but out of date. Upgraded it 5.64.1 → 5.64.2 with Homebrew. The repo was linked to `incredible-truth` / `production` with **no service**; re-linked with `--service career-platform`, so `railway` commands in the repo now default to the web service. The link is saved in the CLI's own config; no files were added to the repo. Nothing on Railway was changed.
- **2026-10-10:** `railway deployment list`: the latest deployment `cdd06c1f` is **SUCCESS** at 17:11 PDT, built from branch **`railway-postgres`** commit `8557f28` (not `main`; I didn't trigger it). The 4 earlier deploys (main) FAILED. Build: Railpack, `pip install -r requirements.txt`, with psycopg 3.3.6. Runtime: `Uvicorn running on http://0.0.0.0:8080`, 2 workers, startup complete, `GET /` returns 200. Domain: custom `zetiantao.me` (target port 8080, verified, certificate valid, CNAME @ → `xuwtdiji.up.railway.app`); there's no Railway-generated domain. `https://zetiantao.me/` returns 200 and shows real profile data. **Security: the web service still has only `DATABASE_URL`, so the live `/admin` uses the code defaults (`admin` / `change-me`).** Not tested against production.
- **2026-10-10:** At your request, **removed the `/admin` editor** on branch `railway-postgres` (not yet committed). Deleted `app/routes/admin.py`, `app/services/admin.py` and `app/templates/admin/*`; removed the router include, the `admin_username/admin_password/session_secret` settings, and their entries in `.env.example`, `README.md` and `tests/conftest.py`; updated `PRODUCT.md`. Replaced the admin tests with `test_admin_area_is_removed` (5 cases, all 404), which failed before the change. Suite: 26 passed, 1 skipped. Locally on the rehearsal Postgres, all public pages return 200, and `/admin`, `/admin/login` and `POST /admin/login` return 404. This closes the default-password exposure once deployed, so the `ADMIN_*`/`SESSION_SECRET` steps in section 2.1 no longer apply. From now on, content is edited in the database directly. Left as is: the admin styles in `site.css` and `DESIGN.md` (unused), and `python-multipart` (no longer needed).
- **2026-10-10:** Committed and pushed `2a4e2c4` "Remove the /admin editor" (you approved). Railway deployed it from `railway-postgres` (`4dcefe0b`, **SUCCESS** 17:33 PDT; the previous `cdd06c1f` is now REMOVED). Live check on `https://zetiantao.me`: `/`, `/resume`, `/portfolio` and `/healthz` return 200; `/admin`, `/admin/login` and `POST /admin/login` return **404**. The default-password exposure is closed.
- **2026-10-10:** At your request, added skill **Chinese** to Railway Postgres via `railway connect Postgres` (psql over the public TCP proxy), in one transaction guarded against duplicates: id 10, category `languages`, proficiency NULL (not given), `published`, sort_order 9. It shows on the live `/` and `/resume` under a new heading **"Languages skills"**. The heading template is `{{ label }} skills`, and category `language` would put it under "Technical" (`SKILL_GROUPS`). **Railway now differs from the VM** (10 skills vs 9). Railway is the source of truth from here; the VM DB is no longer kept in sync.
- **2026-10-10:** Rewrote `README.md` to match how the site runs on Railway: the architecture; deploys from `railway-postgres`; Railpack building from `requirements.txt`; the `railway.json` settings; `DATABASE_URL` as the only variable; the domain and DNS; CLI checks; editing content through `railway connect Postgres` now that there's no admin; regenerating the fallback snapshot; the known DB-down limitation; and the VM history. Checked the commands it shows: the old `python scripts/seed_demo.py` was **broken** (`No module named 'app'`), so it's now `python -m scripts.seed_demo`; the local seed and run steps work (`/` returns 200); `generate_snapshot` works against Postgres (tested into a temp file). Tests: 26 passed, 1 skipped. Uncommitted. Not updated: `PRODUCT.md` still says Azure VM / SQLite and "maintains content through the admin area".
- **2026-10-10:** You asked to commit and push everything and merge to `main`. Committed the README, this plan and the Azure plan's 2026-10-05 log line on `railway-postgres`, pushed it, merged it into `main` with `--no-ff` (as with the earlier PR merges) and pushed `main`. `docs/evidence/ex03.md` (your unfinished coursework edit) and `.claude/` were left uncommitted.
