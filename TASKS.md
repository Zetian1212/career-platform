# Project 1 gaps

From the requirements audit on 2026-10-20 (repo at `1e1fa9d`). Most urgent first.

## Urgent

- [ ] Deploy `260d6c9` on Railway: auto-deploy didn't fire. Check: `railway redeploy --from-source --yes --service career-platform`, then `railway deployment list` shows `SUCCESS` for `1e1fa9d`
- [ ] Record the live result of `260d6c9` (commit SHA, Railway deployment ID, observed behaviour at https://zetiantao.me): README.md → "A reviewed change through Railway"
- [ ] Find out why the push to `main` didn't auto-deploy: Railway dashboard → career-platform → Settings → Source (branch, auto-deploy, "wait for CI")
- [ ] Fill in the final commit SHA: docs/project-1-submission.md (`git rev-parse HEAD` on `main`)
- [ ] Rewrite the Reflection in your own words: README.md → "Reflection"
- [ ] Review and rewrite the Decisions in your own words: README.md → "Decisions"

## 1. Personal application

- [ ] Confirm the live site returns 503 + "Projects temporarily unavailable." on a DB failure (only tested locally): docs/evidence/db-outage-check.md → "On Railway"
- [ ] Confirm the "website as a project in progress" entry exists in production Postgres: `railway connect Postgres` → `select title, summary, state from project;`

## 2. Azure deployment

- [ ] Add the `Allow-HTTPS-443` rule to the NSG table: docs/superpowers/plans/2026-10-01-operate-the-vm.md → "Inbound rules"
- [ ] Restart test after HTTPS was set up (needs the VM started): docs/superpowers/plans/2026-10-01-operate-the-vm.md → "Restart check"
- [ ] Decide whether to start the VM again (the assignment says keep it running; deallocated since 2026-10-13): README.md → "The Azure deployment"

## 3. Domain and HTTPS

- [ ] Save a screenshot or export of the Cloudflare `www` redirect rule: docs/evidence/img/ + README.md → "Domain and HTTPS"
- [ ] Re-run the `dig`/`curl`/`openssl` checks and update the dated output: README.md → "Domain and HTTPS"

## 4. Railway/PostgreSQL migration

- [ ] Save the raw source/target comparison output (or the script that produced it): docs/evidence/ + link from README.md → "The Railway migration"
- [ ] Add evidence that the rendered pages match between VM and Railway (screenshots or saved HTML): docs/evidence/
- [ ] Rehearse the rollback, or keep it labelled unrehearsed: README.md → "Rolling back"

## 5. Verified website update

- [ ] Record the live behaviour seen after `630fbfe` / deployment `685e06f6`: README.md → "A reviewed change through Railway"

## 6. Zoho email

- [ ] Add the send date of the before-MX message (from the Office 365 Sent folder or the bounce headers): docs/evidence/ex06.md
- [ ] Do a separate header check, or note that it reuses the Oct 17 header: docs/evidence/zoho-header-check.md
- [ ] Review a DMARC aggregate report sent to zetian@zetiantao.me: docs/evidence/zoho-header-check.md → "What this proves"

## 7. GA4

- [ ] Confirm the action you performed (accepted the banner, clicked LinkedIn and GitHub) and the date of the screenshots: README.md → "Analytics and privacy", docs/evidence/ex06.md §3

## 8. Engineering record

- [ ] Confirm the Railway trial end date in the dashboard: README.md → "Costs, expiry and cleanup"
- [ ] Record the Azure for Students credit balance (portal): README.md → "Costs, expiry and cleanup"
- [ ] Record the domain price (Namecheap order): README.md → "Costs, expiry and cleanup"
- [ ] Update PRODUCT.md (it still describes the Azure VM and the admin area): PRODUCT.md
- [ ] Optionally write up the real SSH/NSG network failure on its own (it's only in the plan log): README.md → "Investigated failures"
- [ ] Read every agent-written claim in the README and fix anything you can't explain: README.md
