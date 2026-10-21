# Database outage: empty table, failure and recovery

Requirement 1 asks for this behaviour: when the database fails, the profile stays visible, the page says "Projects temporarily unavailable." and returns HTTP 503. A healthy request returns 200. When the database comes back, a refresh restores the projects without restarting the app. An empty table is a normal, healthy page.

## The failure (found 2026-10-10, real, not a lab exercise)

**Symptom.** While checking the Railway branch (see the 2026-10-10 entry "(3) Pages load with the DB down: FAIL" in [the migration plan](../superpowers/plans/2026-10-08-railway-postgres-migration.md#progress-log)), I stopped a local Postgres with `pg_ctl stop -m fast` while the app was running. `/`, `/resume`, `/portfolio` and `/portfolio/career-platform` returned **500** (`psycopg.OperationalError`). `/contact` and `/healthz` still returned 200.

**Checks and diagnosis.**
- The snapshot fallback (`app/static/fallback/profile.json`) only wrapped the profile query. After it, each route called `repo.list_projects()`, `list_skills()`, `list_experience()` and the others with no error handling, so the first of those calls raised and FastAPI turned it into a 500.
- With the database down at **startup**, `init_db()` in `create_app()` raised, so no worker started and nothing was served.
- A first attempt used `brew services stop`, which waits for open connections to close, so the app kept getting answers. I threw that result away and used `pg_ctl stop -m fast`.

**Repair (2026-10-20).** In `app/routes/public.py`, the content queries for `/`, `/resume`, `/portfolio` and `/portfolio/{slug}` are wrapped in `except SQLAlchemyError`. On failure, the page renders the profile from the snapshot with no projects, shows "Projects temporarily unavailable." (on `/resume`: "Experience and certifications temporarily unavailable."), and returns **503**. It never fills in sample content. In `app/main.py`, a database error during startup is logged and the app starts anyway. Recovery needs no new code: `pool_pre_ping=True` on the cached engine (`app/db.py`) throws away dead connections and opens new ones on the next request.

The empty-table case already worked. With zero published projects, `/` and `/portfolio` say "Projects will appear here as they are published." and return 200.

## Repeated check

### Automated (SQLite)

`tests/test_public_routes.py` has two new tests:

- `test_empty_project_table_is_a_healthy_page`: an empty database gives 200 and the "will appear" text.
- `test_database_outage_keeps_profile_and_returns_503`: the app starts while its database file can't be opened. `/`, `/portfolio`, `/portfolio/career-platform` and `/resume` return 503 with the snapshot name and the "temporarily unavailable" text, while `/healthz` returns 200. Then the database is created inside the same running app, and `/` and `/portfolio` return 200.

Before the fix, the outage test **failed** (`sqlalchemy.exc.OperationalError: unable to open database file`, raised from `create_app()`). With the fix: `30 passed, 1 skipped`.

### Manual, against real PostgreSQL 16 (laptop, 2026-10-20, times UTC)

Setup: a throwaway database `outage_test`, loaded with demo content (`scripts.seed_demo` into SQLite, then `scripts.copy_sqlite_to_postgres`). The app ran as `uvicorn app.main:create_app --factory --port 8791 --workers 2`. The demo profile is "Demo"; the snapshot profile is "Zetian", so the heading shows which source answered.

```
== healthy
20:33:49 /          200  <h1 id="profile-name">Hi, I'm Demo.
20:33:50 /portfolio 200  <h1>Portfolio
20:33:50 /resume    200  <h1>Resume
20:33:50 /healthz   200
== pg_ctl stop -m fast
20:33:50 /          503  <h1 id="profile-name">Hi, I'm Zetian.|Cached profile is showing while the database is unavailable.|Projects temporarily unavailable.
20:33:50 /portfolio 503  <h1>Portfolio|Cached profile is showing while the database is unavailable.|Projects temporarily unavailable.
20:33:50 /resume    503  <h1>Resume|Cached profile is showing while the database is unavailable.|Experience and certifications temporarily unavailable.
20:33:50 /healthz   200
== pg_ctl start
20:33:52 /          200  <h1 id="profile-name">Hi, I'm Demo.
20:33:52 /portfolio 200  <h1>Portfolio
20:33:52 /resume    200  <h1>Resume
20:33:52 /healthz   200
== uvicorn PIDs before and after: 45950 45952 45953 (unchanged, so no restart)
```

Starting the app while Postgres was already down:

```
== app started while DB down
20:34:07 /        503
20:34:07 /healthz 200
("Database unavailable at startup" logged)
== DB started
20:34:09 /        200
```

The throwaway database was dropped afterwards, and the Homebrew Postgres service was restarted as it was before.

### On Railway, production (2026-10-21, times UTC)

The live app is deployment `08f4c6f6` (`c298f5d`, which contains the fix `260d6c9`). I restarted the production Postgres service with `railway service restart --service Postgres` while polling `https://zetiantao.me/` from my laptop every half second. Each line shows the time, the HTTP status, and which outage text was on the page. Nothing was deleted; the data lives on Postgres's volume.

```
00:37:17.881 200
00:37:18.501 200
00:37:19.135 503 Cached profile is showing|Projects temporarily unavailable.|
00:37:20.833 200
00:37:21.594 200
```

The poll ran from 00:36:58 to 00:39:33: 31 × 200, then 1 × 503, then 203 × 200.

Postgres's own log (`railway logs --service Postgres`) lines up with it:

```
00:37:18.938 LOG:  received fast shutdown request
00:37:18.943 FATAL:  terminating connection due to administrator command   (×2, the app's pooled connections)
00:37:19.002 LOG:  database system is shut down
00:37:20.770 LOG:  starting PostgreSQL 18.6 …
00:37:20.790 LOG:  database system is ready to accept connections
```

- **Failure:** the one request made while Postgres was down (00:37:19.1) got **503** with the cached profile and "Projects temporarily unavailable."
- **Recovery without an app restart:** the next request after Postgres was ready (00:37:20.8) got **200**. The app deployment was `08f4c6f6` (`SUCCESS`) before and after, so only the database restarted.
- **Data intact:** at 00:40 UTC, `/portfolio` listed the `career-platform` project again and `/resume` showed its Experience and Certifications sections.
- **Limits:** the outage lasted about 2 seconds, so only one poll landed in it. `/resume` and `/portfolio` weren't polled during the outage; they were only covered by the local test. The CLI's `restart` command didn't return by itself and was stopped after the restart had finished.

On Railway, the pre-deploy step `python -m scripts.init_db` still fails if the database is down when a deploy starts. That's deliberate: the deploy stops and the previous version keeps serving.

## Remaining limitations

- `/healthz` doesn't check the database, so Railway's health check passes during a database outage. That keeps the profile online, but Railway won't alert on it.
- The snapshot is only as fresh as the last `scripts.generate_snapshot` run.
