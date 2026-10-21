# Project 1 gaps

From the requirements audit on 2026-10-20 (repo at `1e1fa9d`). Most urgent first.

## Urgent

- [x] Deploy `260d6c9` on Railway: auto-deploy didn't fire. Done 2026-10-20: live in deployment `08f4c6f6` (`c298f5d`, SUCCESS 22:05 UTC); all public pages return 200 at 23:57 UTC. Check: `railway redeploy --from-source --yes --service career-platform`, then `railway deployment list` shows `SUCCESS` for `1e1fa9d`
- [x] Record the live result of `260d6c9` (commit SHA, Railway deployment ID, observed behaviour at https://zetiantao.me): README.md → "A reviewed change through Railway"
- [x] Find out why the push to `main` didn't auto-deploy. Closed 2026-10-20 as a one-off: only the `1e1fa9d` push was skipped, and the next three pushes (`c4c4311`, `63e8747`, `c298f5d`) each deployed. The cause isn't visible from the CLI. Recorded in README.md → "A reviewed change through Railway".
- Final commit SHA: moved to "Last step" at the bottom (it has to be done after everything else)
- [x] Rewrite the Reflection in your own words: README.md → "Reflection"
- [x] Review and rewrite the Decisions in your own words: README.md → "Decisions"

## 1. Personal application

- [x] Confirm the live site returns 503 + "Projects temporarily unavailable." on a DB failure. Done 2026-10-21 00:37 UTC: production Postgres restart gave 200 → 503 → 200 with the app unchanged. docs/evidence/db-outage-check.md → "On Railway, production"
- [ ] **Needs you:** label the project entry as in progress. Checked 2026-10-21: the entry exists (live `/portfolio/career-platform`, read from the DB, no banner), but it isn't labelled "in progress" and still says SQLite, admin editor and Azure. Approved fix (title "Career Platform (in progress)" + new summary) is ready to run as one transaction; see "Commands for you" at the bottom. Then check that `/portfolio/career-platform` shows the new title.

## 2. Azure deployment

- [x] Add the `Allow-HTTPS-443` rule to the NSG table. Done 2026-10-21 as a dated addendum, from the Azure activity log (created 2026-10-06 21:38 UTC): docs/superpowers/plans/2026-10-01-operate-the-vm.md → "Inbound rules"
- [x] Restart test after HTTPS was set up: closed, not done. The VM stays deallocated by your decision, and the 2026-10-05 restart evidence stands. Would need the VM started: docs/superpowers/plans/2026-10-01-operate-the-vm.md → "Restart check"
- [x] Decide whether to start the VM again: decided 2026-10-20 to leave it stopped, recorded in the README. (the assignment says keep it running; deallocated since 2026-10-13): README.md → "The Azure deployment"

## 3. Domain and HTTPS

- [x] Save an export of the Cloudflare `www` redirect rule. Done 2026-10-21: docs/evidence/cloudflare-www-redirect.md, linked from README.md → "Domain and HTTPS"
- [x] Re-run the `dig`/`curl`/`openssl` checks. Done 2026-10-21 00:44 UTC, identical results, date added: README.md → "Domain and HTTPS"

## 4. Railway/PostgreSQL migration

- [x] Save the raw source/target comparison output: closed, not possible now. The Oct 8/10 comparison wasn't saved, the source VM is deallocated, and the production DB has no public access. The dated results stay in the migration plan's progress log.
- [x] Rendered-page comparison between VM and Railway: closed, not possible without starting the VM. The plan log records the checked page content (profile, 3 experience entries, 2 schools, 5 certifications).
- [x] Rehearse the rollback, or keep it labelled unrehearsed: kept labelled unrehearsed (rehearsing needs the VM). README.md → "Rolling back"

## 5. Verified website update

- [x] Record the live behaviour of `630fbfe` / deployment `685e06f6`. Done 2026-10-21 00:44 UTC (checked afterwards, labelled as such): README.md → "A reviewed change through Railway"

## 6. Zoho email

- [x] Before-MX message: sent 2026-10-13 21:08:05 UTC, rejected by Namecheap's relay (`554 5.7.1 Relay access denied`), from the bounce details: docs/evidence/ex06.md
- [x] Header check reuses the Oct 17 header: already stated in its first paragraph. docs/evidence/zoho-header-check.md
- [x] DMARC report read (2026-10-21): 2 messages on Oct 17, SPF and DKIM pass, disposition none; XML committed: docs/evidence/zoho-header-check.md

## 7. GA4

- [x] Screenshot date: 2026-10-17, 11:50 and 12:28 PT (file metadata), committed in `8e71c76`: README.md → "Analytics and privacy"
- [x] Action confirmed by me on 2026-10-20: accepted the banner, browsed, clicked LinkedIn and GitHub: README.md → "Analytics and privacy"

## 8. Engineering record

- [x] Railway trial end date. Done 2026-10-21 from the Railway API: 16 days remaining, so it ends about 2026-11-06. README.md → "Costs, expiry and cleanup"
- [x] Azure for Students credit: $95 of $100 left (portal, 2026-10-20): README.md → "Costs, expiry and cleanup"
- [ ] **Needs you:** record the domain price (Namecheap order): README.md → "Costs, expiry and cleanup"
- [x] Update PRODUCT.md. Done 2026-10-21: Railway + PostgreSQL, no admin, 503 outage behaviour, Privacy page, GA consent.
- [x] SSH/NSG network failure: closed. It's row 4 of README.md → "Investigated failures", linked to the dated log entry, which is enough for an optional item.
- [ ] **Needs you:** read every agent-written claim in the README and fix anything you can't explain: README.md
- [ ] **Needs you:** Decision 4 (your words) says you edit with `railway connect Postgres`. The public proxy that used is gone; the README's Editing content section now says `railway ssh`. Update your sentence if you want them to match.
- [ ] **Needs you:** test the README's new `railway ssh` commands (psql, `pg_dump`, snapshot). They're marked untested. Running the project update below tests the first one.

## Last step (after every other change is committed)

- [ ] Fill in the final commit SHA. A file can't contain the SHA of the commit that holds it, so: (1) commit and push all remaining work; (2) `git rev-parse HEAD` gives X; (3) in docs/project-1-submission.md, set "Final commit" to X, noting that the next commit only records this SHA; (4) commit and push that one-line change; (5) submit X in Brightspace, so the index and Brightspace match. Check: `git diff X HEAD` shows only that line.

## Commands for you

**Project entry "in progress" (task above).** Run this in your own terminal, in the repo folder. The first time, type `yes` to accept Railway's host key. It prints the old row (keep the output for rollback), updates one row in a transaction, and prints the new row:

```bash
railway ssh --service Postgres -i ~/.ssh/railway_career_platform -- \
  'psql -U "$PGUSER" -d "$PGDATABASE" -X' <<'SQL'
\pset pager off
\x on
\set ON_ERROR_STOP 1
BEGIN;
-- Old values, kept in the terminal output for rollback
SELECT id, slug, title, summary, updated_at FROM project WHERE slug = 'career-platform';
UPDATE project
SET title = 'Career Platform (in progress)',
    summary = 'This website, and a project in progress. A FastAPI and Jinja resume and portfolio site, built in GitHub Codespaces, run on an Azure Ubuntu VM with SQLite, and now on Railway with PostgreSQL. Pages read from the database on every request, with a cached profile if the database is down. It will grow into a career platform through the semester.',
    updated_at = now()
WHERE slug = 'career-platform' AND title = 'Career Platform';
SELECT id, slug, title, summary, updated_at FROM project WHERE slug = 'career-platform';
COMMIT;
SQL
```

Expected: `UPDATE 1` then `COMMIT`. `UPDATE 0` means the title had already changed, and nothing was modified. If the piped file doesn't reach psql, open a shell with `railway ssh --service Postgres -i ~/.ssh/railway_career_platform`, run `psql -U "$PGUSER" -d "$PGDATABASE"`, and paste the SQL between the `SQL` markers.
