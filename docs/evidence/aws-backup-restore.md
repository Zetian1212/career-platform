# Railway backup and restore test (before the AWS migration)

2026-10-31. Session 17, section 2. Railway was not changed.

## Backup

- **Taken:** 2026-10-31 21:20:02 UTC, from Railway Postgres 18.6 (`incredible-truth` / `production`).
- **Route:** `railway connect Postgres --tunnel-only` (SSH tunnel). The service has no public TCP proxy, and none was enabled. The tunnel was closed after use.
- **Tool:** `pg_dump` 18.6 (Homebrew `postgresql@18`), matching the server. The installed 16.x tools can't dump an 18 server.
- **Command:** `pg_dump --format=custom --no-owner --no-privileges`
- **File:** `~/backups/career-railway-20261031T212002Z.dump`, 26,717 bytes, mode 600, outside the repo. SHA-256 `fa821306…3632426`. 9 `TABLE DATA` entries.
- **Uploaded files:** none to back up. The app has no upload route, `media_asset` has 0 rows, and `app/static` is in Git.

Rows at backup time: profile 1, experience 5, education 2, skill 26, project 2, certification 8, link 3, media_asset 0, project_skill 0.

## Restore test

- **Target:** a new throwaway Postgres 18.6 cluster on this laptop (port 5433, socket only), database `career_restore_test`. Railway wasn't queried during the restore or the app checks.
- **Restore time:** 0.06 s (`pg_restore --no-owner --no-privileges --exit-on-error`).
- **Data:** every one of the 9 tables matched Railway row for row. Each side was hashed as `md5(string_agg(row::text ORDER BY row::text COLLATE "C"))` with `PGTZ=UTC`. The source hashes are saved next to the dump. Sequences were at `max(id)` for every table.
  - The first comparison showed false mismatches. Timestamps were rendered in local time (EDT) instead of UTC, and macOS and Linux sort text differently under their default collations. Pinning UTC and `COLLATE "C"` removed both differences.
- **App:** ran `uvicorn app.main:create_app` with `DATABASE_URL` pointing at the restored database. Two clean runs: `/`, `/resume`, `/portfolio`, both `/portfolio/<slug>` pages, `/contact` and `/privacy` all returned 200 with database content (resume skills present, no degraded banner), and an unknown path returned 404.
  - The first app run returned 404 on `/portfolio/career-platform` and matched "degraded/unavailable" on the home page. The next three runs didn't reproduce it, and that log wasn't kept. Cause *unverified*.

## Still open

- [ ] Second copy on independent storage (not this laptop's disk).
- [ ] Backup frequency and retention. Currently manual only. See "Known gaps" in the README.
- [ ] RPO / RTO decision.
