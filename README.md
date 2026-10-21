# career-platform

A FastAPI + Jinja resume and portfolio site for Zetian Tao. Live at **https://zetiantao.me**, running on Railway with PostgreSQL. It started in Codespaces with SQLite, moved to an Azure Ubuntu VM (nginx + uvicorn + SQLite), and on 2026-10-10 moved to Railway + PostgreSQL. It is the starting point for the career platform built through the semester.

The site shows my profile, education, experience, skills, certifications and links. Projects and the rest of the content are read from the database on every request. A cached copy of the core profile (`app/static/fallback/profile.json`) keeps the page useful when the database is down: the site returns **503** with "Projects temporarily unavailable." and recovers on the next refresh once the database is back ([check](docs/evidence/db-outage-check.md)).

**Project 1 submission index:** [docs/project-1-submission.md](docs/project-1-submission.md)

> Sections marked *(written afterwards)* were reconstructed on 2026-10-20 from the plans, git history and saved evidence, with help from Claude Code. They are not plans made before the work. The plans themselves are under [`docs/superpowers/`](docs/superpowers/) and kept as written, with dated progress logs.

## Contents

- [Architecture](#architecture): Azure, Railway, email and analytics diagrams
- [How it runs on Railway](#how-it-runs-on-railway)
- [Domain and HTTPS](#domain-and-https)
- [Email](#email)
- [Analytics and privacy](#analytics-and-privacy)
- [Setting up and updating](#setting-up-and-updating): local dev, tests, content, deploys
- [A reviewed change through Railway](#a-reviewed-change-through-railway)
- [Rolling back](#rolling-back): code and data
- [The Azure deployment](#the-azure-deployment)
- [The Railway migration](#the-railway-migration): data preservation and who manages what
- [Decisions](#decisions)
- [Investigated failures](#investigated-failures)
- [Costs, expiry and cleanup](#costs-expiry-and-cleanup)
- [Limitations](#limitations)
- [Reflection](#reflection)
- [Docs and records](#docs-and-records)

## Architecture

### Now: Railway (since 2026-10-10)

```
                         Cloudflare DNS (authoritative for zetiantao.me)
                         ─────────────────────────────────────────────────
                         zetiantao.me      CNAME → xuwtdiji.up.railway.app   DNS only
                         www.zetiantao.me  A → 172.183.16.158                proxied (redirect rule)
                         MX → mx.zoho.com / mx2 / mx3                        DNS only
                              │ (1) DNS lookup, UDP/TCP 53
Visitor's browser ────────────┘
   │
   │ (2) https://zetiantao.me   TCP 443, TLS 1.3, cert CN=zetiantao.me (Let's Encrypt, issued by Railway)
   ▼
Railway edge proxy (US West, "railway-hikari") ── terminates TLS
   │ (3) plain HTTP over Railway's internal network, to $PORT (8080)
   ▼
Railway project "incredible-truth" / production
   career-platform service: uvicorn manager + 2 workers (FastAPI)
   │ (4) PostgreSQL protocol, TCP 5432, private network (postgres.railway.internal)
   ▼
   Postgres service (PostgreSQL 18, Railway volume)

http://zetiantao.me ─▶ Railway edge ─▶ 301 to https://zetiantao.me/
http(s)://www.zetiantao.me ─▶ Cloudflare edge (cert *.zetiantao.me) ─▶ 301 to https://zetiantao.me/<same path>
                               (the redirect is answered at Cloudflare; the VM behind the www record isn't contacted)

GitHub repo Zetian1212/career-platform ──push to main──▶ Railway build (Railpack) ─▶ pre-deploy init_db ─▶ /healthz check ─▶ live
```

### Before: Azure VM (2026-09-29 to 2026-10-10)

```
Visitor's browser
   │ DNS: zetiantao.me and www → A 172.183.16.158 (DNS only)
   │ TCP 80 (redirects to HTTPS) / TCP 443 (TLS, Let's Encrypt cert from certbot)
   ▼
Azure NSG vm-career-platformNSG (North Central US)
   allows 22 from my IPs only, 80 and 443 from anywhere; everything else dropped
   ▼
vm-career-platform, Ubuntu 24.04, public 172.183.16.158 / private 10.0.0.4
   nginx (0.0.0.0:80, :443) ── terminates TLS
     │ plain HTTP, 127.0.0.1:8000 (never leaves the VM)
     ▼
   systemd career-platform.service → uvicorn manager + 2 workers (user azureuser)
     │ file access, no network
     ▼
   SQLite ~/career-platform/career_platform.db

Admin: laptop ──SSH TCP 22, key only──▶ azureuser@172.183.16.158
```

Details, commands and the restart test are in the [operate-the-VM plan](docs/superpowers/plans/2026-10-01-operate-the-vm.md). The VM has been **deallocated since 2026-10-13** (see [The Azure deployment](#the-azure-deployment)).

### Email path

```
Inbound:  outside sender's server ─(DNS: MX zetiantao.me → mx.zoho.com)─▶ SMTP TCP 25 ─▶ Zoho Mail (US data center) ─▶ my Zoho inbox
Outbound: Zoho webmail (HTTPS) ─▶ Zoho's SMTP servers (e.g. 165.173.180.52), DKIM-signed with selector zmail
              ─▶ SMTP TCP 25 ─▶ recipient's server, which checks:
                   SPF   TXT zetiantao.me           "v=spf1 include:zohomail.com ~all"
                   DKIM  TXT zmail._domainkey       Zoho's public key
                   DMARC TXT _dmarc                 "v=DMARC1; p=none; rua=mailto:zetian@zetiantao.me"
```

Mail never touches Railway or the VM. Only the DNS records connect the domain to Zoho.

### Analytics path

```
Visitor's browser
  1. GET https://zetiantao.me/ (Railway) → HTML + /static/js/analytics.js (data-ga-id="G-3XLF72EHQC")
  2. analytics.js sets Consent Mode defaults to "denied" and shows the banner. Nothing is sent to Google yet.
  3. Visitor clicks Accept → the browser loads gtag.js from https://www.googletagmanager.com (TCP 443)
  4. gtag sends events (page_view, scroll, click …) straight from the browser to
     https://region1.google-analytics.com/g/collect (TCP 443). The Railway server never sees these.
  5. GA4 property → Realtime report (seconds) → standard reports (hours later)
```

## How it runs on Railway

- **Deploys:** the `career-platform` service builds from this GitHub repo's **`main`** branch. A push to `main` triggers a new deploy. (It deployed the `railway-postgres` branch through 2026-10-11; `railway deployment list` shows `main` from deploy `685e06f6` on 2026-10-17 onward.)
- **Build:** Railpack detects Python 3.12 (`.python-version`) and installs `requirements.txt`, so keep `requirements.txt` in step with `pyproject.toml` / `uv.lock`.
- **Deploy settings** live in `railway.json`:
  - pre-deploy: `python -m scripts.init_db` creates any missing tables before the new version starts. It never alters or drops existing ones. If the database is down, it fails, and the previous deployment keeps serving.
  - start: `uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers`. Railway terminates HTTPS and assigns the port (8080 at the moment).
  - health check: `GET /healthz` must return 200 within 60 s. The service restarts on failure, up to 5 times.
- **Variables** on the `career-platform` service (set in the Railway dashboard; nothing secret is in git):

  | Variable | Value |
  |---|---|
  | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (private network). A `postgresql://` URL is switched to the psycopg driver automatically. |
  | `GA_MEASUREMENT_ID` | Optional. Not set, so the default from `app/config.py` (`G-3XLF72EHQC`) is used. Set it to an empty string to turn Google Analytics off. |

  Nothing else is needed. If `DATABASE_URL` is missing, the app quietly falls back to a local SQLite file, which on Railway is empty, so keep it set.

Railway warns that `railway.json` (config as code) is deprecated in favour of `.railway/railway.ts`. Existing files keep working until 2026-12-01.

### Checking on it

With the [Railway CLI](https://docs.railway.com/cli) logged in and linked (`railway link --project incredible-truth --environment production --service career-platform`):

```bash
railway deployment list          # recent deploys and their status
railway logs --build <deploy-id> # build log
railway logs --deployment <deploy-id> # runtime log
railway domain list              # domains (a bare `railway domain` CREATES one)
railway usage                    # spend in the current billing period
curl https://zetiantao.me/healthz
```

## Domain and HTTPS

`zetiantao.me` is registered at Namecheap (2026-10-05, expires 2027-10-05). Its nameservers are Cloudflare's (`bailey.ns.cloudflare.com`, `rudy.ns.cloudflare.com`), so Cloudflare is authoritative.

**Web records** (Cloudflare CLI listing, 2026-10-20):

| Type | Name | Content | Proxy | Purpose |
|---|---|---|---|---|
| CNAME | `zetiantao.me` | `xuwtdiji.up.railway.app` | DNS only | Sends the bare domain to Railway. DNS only, so TLS goes straight to Railway, which holds the certificate. Created 2026-10-11 00:22 UTC (the cutover; before that, the apex was an A record to the VM). |
| TXT | `_railway-verify` | `railway-verify=7253d9…` | DNS only | Proves to Railway that I control the domain. |
| A | `www` | `172.183.16.158` | **Proxied** | Exists only so Cloudflare answers `www` and can apply the redirect rule. The redirect fires at Cloudflare's edge, so it keeps working while the VM is stopped. |

**Redirect rule** (zone ruleset `http_request_dynamic_redirect`, "Redirect from WWW to root"; full export in [cloudflare-www-redirect.md](docs/evidence/cloudflare-www-redirect.md)): if `http.request.full_uri` matches `http*://www.*`, return **301** to `https://${2}`, keeping the path. Query strings aren't preserved by the rule's setting, although the check below shows `?x=1` kept because the wildcard copies the whole URI.

**Verification (2026-10-20, 20:25 UTC, from my laptop; re-run 2026-10-21 00:44 UTC with identical results):**

```
$ dig +short zetiantao.me A            → 69.46.46.100        (Railway, via the CNAME)
$ dig +short www.zetiantao.me A        → 104.21.25.244, 172.67.168.49   (Cloudflare edge)
https://zetiantao.me/                  -> 200
http://zetiantao.me/                   -> 301 https://zetiantao.me/
http://www.zetiantao.me/               -> 301 https://zetiantao.me/
https://www.zetiantao.me/              -> 301 https://zetiantao.me/
https://www.zetiantao.me/resume?x=1    -> 301 https://zetiantao.me/resume?x=1
$ curl -sI https://zetiantao.me/       → HTTP/2 405 (the app only allows GET; GET returns 200), server: railway-hikari, x-railway-edge: lax1

$ openssl s_client -connect zetiantao.me:443 -servername zetiantao.me | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
subject=CN=zetiantao.me
issuer=C=US, O=Let's Encrypt, CN=YE1
notBefore=Oct 10 23:29:25 2026 GMT
notAfter=Jan  8 23:29:24 2027 GMT
X509v3 Subject Alternative Name: DNS:zetiantao.me

$ openssl s_client -connect www.zetiantao.me:443 -servername www.zetiantao.me | openssl x509 …
subject=CN=zetiantao.me
issuer=C=US, O=Let's Encrypt, CN=YE1
notBefore=Oct  5 22:31:31 2026 GMT
notAfter=Jan  3 22:31:30 2027 GMT
X509v3 Subject Alternative Name: DNS:*.zetiantao.me, DNS:zetiantao.me
```

**The certificates.**
- **Bare domain (Railway):** hostname `zetiantao.me` only, Let's Encrypt, valid 2026-10-10 to 2027-01-08 (90 days). Railway issued it after verifying the CNAME and TXT, and it renews automatically. That only works while the CNAME stays **DNS only**, so Railway can answer the certificate challenge. I don't run certbot for it.
- **`www` (Cloudflare edge):** Cloudflare's Universal SSL certificate for `*.zetiantao.me` and `zetiantao.me`, valid to 2027-01-03, renewed by Cloudflare. It covers the redirect only.
- **Azure (before the cutover):** certbot on the VM issued `zetiantao.me` + `www.zetiantao.me` (valid 2026-10-06 to 2027-01-04), renewed by `certbot.timer` through nginx on port 80. My own explanation of HTTPS on the VM, for Exercise 04: [how-this-site-is-secured.md](docs/how-this-site-is-secured.md).

## Email

`zetian@zetiantao.me` is hosted on Zoho Mail (Forever Free plan, 5 GB, US data center; account created 2026-10-13). Cloudflare is still the DNS provider. The zone has Zoho's MX records (`mx.zoho.com` 10, `mx2.zoho.com` 20, `mx3.zoho.com` 50), SPF `v=spf1 include:zohomail.com ~all`, a DKIM key under the `zmail` selector, DMARC `v=DMARC1; p=none; rua=mailto:zetian@zetiantao.me`, and a `zoho-verification` TXT record. They were published 2026-10-13 between 21:23 and 22:00 UTC. Before that, mail went to Namecheap forwarding; the old records are saved in [dns-before-zoho.md](docs/evidence/dns-before-zoho.md) in case they need restoring.

- Delivery tests (before-MX bounce, inbound, reply, new outbound): [ex06.md](docs/evidence/ex06.md)
- What each record does, and the SPF/DKIM/DMARC header analysis (all pass): [zoho-header-check.md](docs/evidence/zoho-header-check.md)

## Analytics and privacy

The site uses Google Analytics 4 (`G-3XLF72EHQC`), but only after a visitor agrees to it.

- `app/static/js/analytics.js` is loaded on every page when `ga_measurement_id` is set. It sets Consent Mode v2 defaults to denied and shows a banner. Google's script is loaded only after the visitor clicks **Accept**. **Decline** keeps it off and deletes any `_ga` cookies.
- The choice is kept in `localStorage` under `analytics-consent`. **Cookie settings** in the footer reopens the banner.
- `/privacy` explains what is collected, why and who receives it. The `{# VERIFY #}` comments in `app/templates/public/privacy.html` list the GA property settings the page assumes (only page views, scrolls and outbound clicks in enhanced measurement, Google signals off, 2-month retention). If you change those settings in GA, update the page.
- The stylesheet and the analytics script are linked with a `?v=` hash of their contents, so a deploy that changes them busts browser caches.

**Verification (2026-10-17, GA4 Realtime; screenshots in [ex06.md](docs/evidence/ex06.md#3-google-analytics)).**
- *Action:* on https://zetiantao.me I accepted the banner, browsed a few pages, then clicked my LinkedIn and GitHub profile links.
- *Observed:* Realtime "Event count by Event name" showed `page_view` 8, `scroll` 6, `user_engagement` 6, `click` 3, `first_visit` 1 and `session_start` 1. Drilling into `click` showed `link_domain` = `linkedin.com` and `github.com`, `link_url` = my two profile URLs, and `outbound` = `true`. That's GA4 enhanced measurement's outbound-click event, so it needed no custom code.
- *Why it's useful:* the site exists so recruiters and others can find me. A page view says someone arrived. An outbound click to LinkedIn or GitHub says they went on to look at my work, which is the action I actually care about. Over time, `link_domain` shows which profile people choose.
- *What the checks show:* the browser → Google path in the [analytics diagram](#analytics-path) works end to end on the production domain, consent gating doesn't block collection after Accept, and the event carries enough parameters to tell links apart. They don't show visitor counts or that Decline sends nothing. That was checked in code (`tests/test_public_routes.py::test_analytics_script_defaults_to_denied`), not in GA.

## Setting up and updating

### Local development

```bash
uv sync
DATABASE_URL=sqlite:////tmp/career-local.db uv run python -m scripts.seed_demo --reset
DATABASE_URL=sqlite:////tmp/career-local.db uv run uvicorn app.main:create_app --factory --reload --port 8000
```

Then open http://localhost:8000 and check `/healthz`. The analytics banner shows up locally too; add `GA_MEASUREMENT_ID=` to the commands to keep local visits out of Google Analytics.

- `scripts/seed_demo.py` loads demo content. It only works on SQLite and refuses any other URL, so it can't touch production.
- The local database lives in `/tmp` so it stays out of the repo. Don't point it at `career_platform.db`, which is tracked in git (an empty leftover from the SQLite days).

### Tests

```bash
uv run pytest -q
```

To also run the Postgres copy test, point `TEST_POSTGRES_URL` at a throwaway database whose name ends in `_test`, for example a local Postgres: `TEST_POSTGRES_URL=postgresql://$USER@localhost/career_test uv run pytest -q`.

### Shipping a code change

1. Work on a branch. Run `uv run pytest -q` and look at the change locally (above).
2. Review the diff: `git diff main...` (or open a PR on GitHub and read it there).
3. Merge to `main` and push. Railway builds, runs the pre-deploy step, waits for `/healthz`, then switches traffic over. The old deployment serves until then.
4. Check `railway deployment list`: the new deploy should be `SUCCESS` with your commit SHA. Then check the behaviour at https://zetiantao.me.

### Editing content

There is no admin area; `/admin` was removed on 2026-10-10. Content lives in the Railway Postgres, and you edit it there directly.

The Postgres service no longer has a public TCP proxy (found 2026-10-21; `railway tcp-proxy list --service Postgres` lists none, and `DATABASE_PUBLIC_URL` is gone). Nothing outside Railway can reach the database, which is safer. It also means `railway connect Postgres` from the laptop, used up to 2026-10-10, no longer has a public address to go through. Open `psql` inside the Postgres container instead, using an SSH key registered with Railway (`railway ssh keys add`; mine is `~/.ssh/railway_career_platform`, added 2026-10-21):

```bash
railway ssh --service Postgres -i ~/.ssh/railway_career_platform   # accept the host key the first time
psql -U "$PGUSER" -d "$PGDATABASE"                                # inside the container
```

*Untested by me as of 2026-10-21. The first `railway ssh` stopped at host-key verification, which needs a person to accept it.*

For example, the "Chinese" skill was added with:

```sql
INSERT INTO skill (name, category, state, sort_order) VALUES ('Chinese', 'languages', 'published', 9);
```

- Only rows with `state = 'published'` appear on the site.
- Skills are grouped by `category`: `finance` → "Finance", and `tool` / `language` / `library` / `framework` → "Technical". Any other category becomes its own heading, shown as "*Category* skills".
- Changes appear immediately, with no redeploy.
- Take a dump first (see [Rolling back](#rolling-back)) if you're changing more than one row.

### Fallback snapshot

`app/static/fallback/profile.json` is the cached core profile (name, headline, summary, links, top skills, education) that the site falls back on if the database can't be read. The `interests` list is edited in this file by hand. After changing the profile in the database, regenerate the file from the production data and commit it. The script needs a `DATABASE_URL` it can reach. Since the public proxy is gone, either add one for the duration (`railway tcp-proxy create --service Postgres`, use the URL it shows, then `railway tcp-proxy delete`) and run:

```bash
DATABASE_URL='postgresql://…@<proxy-host>:<port>/railway' uv run python -m scripts.generate_snapshot
```

or run `python -m scripts.generate_snapshot` inside the app container (`railway ssh --service career-platform`, which has the private `DATABASE_URL`), print the file with `cat app/static/fallback/profile.json`, and copy it into the repo. *Both routes untested since the proxy was removed.*

## A reviewed change through Railway

**The change:** handle a database outage as requirement 1 asks (503 + "Projects temporarily unavailable.", profile from the snapshot, recovery on refresh, start even if the database is down). Before it, the same outage gave HTTP 500.

- Reviewed: the diff (`app/routes/public.py`, `app/main.py`, three templates, two new tests) was read before committing. The new outage test failed on the old code and passed on the new code. The full suite passed (`30 passed, 1 skipped`), and a manual outage-and-recovery run against a real PostgreSQL 16 passed. All of it is recorded in [db-outage-check.md](docs/evidence/db-outage-check.md).
- **Commit:** `260d6c9bd61d6483b40c27e0b7a13b8d58e7e45d` "Return 503 with the cached profile when the database is down", pushed to `main` on 2026-10-20 (in the push ending `1e1fa9d`).
- **Railway deployment:** the push of `1e1fa9d` didn't start a deploy. The cause isn't visible from the CLI. The next push did, and each one after it too. The change went live in deployment `08f4c6f6-9f49-4d78-aba5-7392d9b45292`, built from `main` at `c298f5d` (which contains `260d6c9`; checked with `git merge-base --is-ancestor`). Status `SUCCESS`, created 2026-10-20 22:05 UTC. Its runtime log shows `Uvicorn running on http://0.0.0.0:8080`, two worker processes and `Application startup complete` twice, with no errors.
- **Live check (2026-10-20, 23:57 UTC, `curl` from my laptop):** `/`, `/resume`, `/portfolio`, `/portfolio/career-platform`, `/contact`, `/privacy` and `/healthz` on https://zetiantao.me all returned **200**. None showed "Projects temporarily unavailable" or the cached-profile banner, so the new code serves the healthy path from the database as before.
- **Outage path checked live (2026-10-21, 00:37 UTC):** I restarted the production Postgres while polling the site every half second. The request during the roughly 2-second outage got **503** with "Projects temporarily unavailable." and the cached profile. The next one got 200, with the app deployment unchanged ([db-outage-check.md](docs/evidence/db-outage-check.md#on-railway-production-2026-10-21-times-utc)).
- **To restore the previous version:** redeploy `de654edf` (`8e71c76`) from the Railway dashboard, or `git revert 260d6c9` and push. No database change is involved. See [Rolling back](#rolling-back).

An earlier change went through the same path: `630fbfe` "Privacy page: GA data retention is 2 months", deployed by Railway as `685e06f6` (branch `main`, 2026-10-17 18:36 UTC). It replaced the placeholder "[2 or 14] months" with "Google Analytics keeps event-level data for 2 months, then deletes it." I didn't record the live page at deploy time. Checked afterwards, on 2026-10-21 00:44 UTC: https://zetiantao.me/privacy returns 200 and shows that exact sentence, with no "[2 or 14]" placeholder.

## Rolling back

*(written afterwards, 2026-10-20)*

### A bad code change

Pick one, fastest first:

1. **Railway redeploy.** Dashboard → `career-platform` → Deployments → the last good deployment (`railway deployment list` shows its commit SHA) → **Redeploy**. It takes about a minute and doesn't change git, so follow up with option 2 or the next push will bring the bad code back.
2. **Revert in git.** `git revert <bad-sha>`, run the tests, push to `main`. Railway deploys the revert like any change. That keeps history honest and is the normal way.
3. If a deploy never becomes healthy, Railway keeps the previous deployment serving. The failed deploy shows `FAILED` and nothing needs rolling back.

Check afterwards: `railway deployment list` shows the expected SHA as `SUCCESS`, `curl -s -o /dev/null -w '%{http_code}' https://zetiantao.me/` returns 200, and the page shows the expected behaviour.

### Database changes

- **Schema.** The app has no migration tool. `scripts.init_db` (`create_all`) only *adds* missing tables, and never alters or drops anything. So rolling code back never needs a schema rollback, and old code keeps working against the newer schema. A change that renames or drops a column would need a hand-written SQL migration plus a dump taken first. There hasn't been one.
- **Data.** Before any manual edit, take a dump outside the repo:

  ```bash
  mkdir -p ~/backups
  railway ssh --service Postgres -i ~/.ssh/railway_career_platform -- \
    'pg_dump -U "$PGUSER" -d "$PGDATABASE" --data-only --format=plain' \
    > ~/backups/career-$(date -u +%Y%m%dT%H%M%SZ).sql
  ```

  Plain SQL format, because a binary dump could be corrupted by the SSH session. *Untested since the public proxy was removed.* Check that the file starts with `-- PostgreSQL database dump` and contains a `COPY public.project` line.

  To undo a bad edit, fix the rows directly in `psql` inside the Postgres container (one transaction). Or empty the tables (`TRUNCATE … RESTART IDENTITY CASCADE`) and replay the dump with `psql -U "$PGUSER" -d "$PGDATABASE" -f <file>`, after copying it into the container or piping it through `railway ssh`. Dumps hold personal data, so they stay out of git (`~/backups` is outside the repo folder).

### Rolling the migration back to Azure

Railway is the source of truth since 2026-10-10, and the VM's SQLite copy is frozen at the 2026-10-08 copy. Going back means carrying over anything written after the cutover:

1. `az vm start -g rg-career-platform -n vm-career-platform`. The public IP is static, and systemd starts nginx and the app at boot (shown in the restart test). Check `curl -I --resolve zetiantao.me:443:172.183.16.158 https://zetiantao.me/`.
2. Find rows written after cutover. Re-run the row-by-row comparison used for the migration (Railway vs. a fresh `.backup` of the VM DB) and list the differences. Known so far: one row, skill `Chinese` (id 10, 2026-10-10). Writes only happen through `psql` (`railway connect Postgres` until 2026-10-10, `railway ssh` into the Postgres container after the public proxy was removed), and only I have access, so there's no visitor data.
3. Apply those rows to the VM DB with `sqlite3`, after taking a `.backup` of it.
4. In Cloudflare, replace the apex CNAME with `A zetiantao.me → 172.183.16.158`, DNS only. The VM's certbot certificate already covers `zetiantao.me` (until 2027-01-04). The `www` redirect rule doesn't change.
5. Verify with `dig`, `curl` and `openssl` as in [Domain and HTTPS](#domain-and-https). Leave Railway running until the VM checks pass.

This hasn't been rehearsed end to end. The individual commands come from the [Azure](docs/superpowers/plans/2026-10-01-operate-the-vm.md) and [migration](docs/superpowers/plans/2026-10-08-railway-postgres-migration.md) records.

## The Azure deployment

Records: [Azure migration plan and log](docs/superpowers/plans/2026-09-24-azure-vm-migration.md) (2026-09-24 to 2026-10-05), [operate-the-VM plan](docs/superpowers/plans/2026-10-01-operate-the-vm.md) (systemd, nginx, NSG, restart test, port/IP/rule record), [ex03](docs/evidence/ex03.md) (VM facts and screenshot), [how-this-site-is-secured.md](docs/how-this-site-is-secured.md) (HTTPS on the VM).

- **VM:** `vm-career-platform`, `Standard_B2ats_v2` (2 vCPU, 1 GiB), Ubuntu 24.04, North Central US. Public IP `172.183.16.158` (Standard, **static**), private `10.0.0.4`.
- **SSH:** `ssh -i ~/.ssh/isba4775_azure azureuser@172.183.16.158`. Key only (password login disabled). The private key is on my laptop, never in the repo.
- **Network rules (NSG `vm-career-platformNSG`, read 2026-10-20):** 300 `Allow-SSH-Laptop` TCP 22 from two `/32` addresses I use; 320 `Allow-HTTP-80` TCP 80 from any; 330 `Allow-HTTPS-443` TCP 443 from any; then Azure's `DenyAllInBound`. No rule for 8000.
- **What stays private:** uvicorn listens on `127.0.0.1:8000` only, and SQLite is a local file, so neither has a network port. nginx on 80/443 is the only public entry point.
- **Service management:** systemd unit `career-platform.service` (`User=azureuser`, `--workers 2`, `Restart=always`, enabled at boot), plus nginx with a `Restart=on-failure` drop-in.
- **Restart evidence (2026-10-05):** after a real reboot at ~21:11 UTC, systemd started the app at 21:11:31 with no manual command, and `curl` through nginx returned 200 with my name from the database. Also killing a worker (no visible effect), killing the manager (502 for about 3 s, then systemd restarted it), and stopping/starting. See the [Restart check](docs/superpowers/plans/2026-10-01-operate-the-vm.md#restart-check).
- **What needed configuration for that:** the systemd unit and `enable` (start at boot), `WorkingDirectory` (relative `.env` and DB paths), `--host 127.0.0.1` (keeps 8000 private), the nginx site with `proxy_pass` and the default site removed, the NSG rule for 80 (later 443), and certbot's nginx plugin for HTTPS.
- **Current state:** **deallocated since 2026-10-13 22:24 UTC**, by my account (Azure activity log). The assignment asks to keep it running. I've chosen to leave it stopped and record that here. Compute charges have stopped, while the disk and static IP still exist, so it can be started again with the same address (rollback step 1). The evidence above was all collected while it was running.

## The Railway migration

Records: [migration plan + progress log](docs/superpowers/plans/2026-10-08-railway-postgres-migration.md) (written 2026-10-08, before any change to the working deployment) and [implementation plan](docs/superpowers/plans/2026-10-08-railway-postgres-implementation.md) (test-first code changes).

**Inventory (from the plan).** Git moved the code, `pyproject.toml`/`uv.lock`/`requirements.txt`, `.python-version`, the templates and static files, the fallback snapshot, and `railway.json` (start command, pre-deploy, health check). Git did **not** move the data (the only real copy was the VM's SQLite file; the git-tracked file is empty), the secrets/configuration (Railway variables: `DATABASE_URL` as a reference to the Postgres service), TLS (Railway issues its own certificate), or DNS (changed in Cloudflare).

**PostgreSQL compatibility changes** (`8557f28`): add `psycopg[binary]` and rewrite `postgresql://` to `postgresql+psycopg://`; pass `check_same_thread` only for SQLite; cache one engine per URL instead of one per request (which would exhaust Postgres connections); bind `0.0.0.0:$PORT`; run `init_db` once as a pre-deploy step so two workers don't race `create_all`; `--proxy-headers` behind Railway's TLS proxy. `scripts/copy_sqlite_to_postgres.py` copies tables in dependency order in one transaction, refuses a non-empty target, and resets the id sequences.

**Preserving current data.**
- *A real change to the original data before the move:* on 2026-10-07 I edited the live VM database: removed the "Source: github.com/…" sentence from the `career-platform` project summary, and set the approved "About me" text in `profile.bio` ([operate-the-VM log](docs/superpowers/plans/2026-10-01-operate-the-vm.md#progress-log), 16:47 and 17:15 UTC). Neither edit exists in the seed script or in git, so a restore from seed data can't match.
- *Copy:* 2026-10-08 21:47 UTC, `sqlite3 .backup` of the live VM DB (SHA-256 `42f9e678…`, integrity ok), copied into Railway Postgres: profile 1, project 1, skill 9, certification 5, education 2, experience 3, link 3, media_asset 0, project_skill 0.
- *Comparison:* against a fresh `.backup` of the live VM DB, on 2026-10-08 and again on 2026-10-10. Every table had equal row counts and **every row was identical in every column** (ordered by primary key, timestamps normalised to UTC). All 8 sequences were past `max(id)`. Result: MATCH. The rendered pages on Railway showed the same profile, 3 experience entries, 2 schools and 5 certifications.
- *Cutover:* 2026-10-10. Railway deploy `cdd06c1f` (`8557f28`) SUCCESS 17:11 PDT. Apex CNAME to Railway created 2026-10-11 00:22 UTC, custom domain verified, certificate valid. Post-cutover checks: `/`, `/resume`, `/portfolio`, `/healthz` 200 with real data. `/admin` removed and checked as 404 (`2a4e2c4`, deploy `4dcefe0b`). See the plan's 2026-10-10 log entries.
- *After cutover:* skill `Chinese` added on Railway only (2026-10-10). Railway is the source of truth, and the VM DB is no longer synced. That's why the rollback above has a "rows written after cutover" step.

**Who manages what** *(written afterwards)*

| Layer | Azure VM | Railway |
|---|---|---|
| Hardware, hypervisor | Azure | Railway (on its cloud provider) |
| OS (Ubuntu patches, users, SSH) | **Me** | Railway (container base image) |
| Runtime (Python version, packages) | **Me** (`uv sync` on the VM) | Railway builds it (Railpack), but **I** choose the version (`.python-version`) and pin packages |
| Process management | **Me** (systemd unit, restarts) | Railway (start command, restart policy, health check), configured by **me** in `railway.json` |
| Web entry point | **Me** (nginx, NSG rules, ports) | Railway edge proxy and `$PORT` |
| TLS certificate and renewal | **Me** (certbot + timer, port 80 open) | Railway (automatic), provided **my** DNS stays correct |
| Application code | **Me** | **Me** |
| Configuration and secrets | **Me** (`.env` on the VM) | **Me**, stored in Railway variables |
| Database software | **Me** (SQLite library, file permissions) | Railway (Postgres image, patching, volume) |
| Data (content, backups, correctness) | **Me** | **Me**: Railway runs Postgres, but dumps, edits and restores are mine |
| DNS | **Me** (Cloudflare) | **Me** (Cloudflare) |
| Cost and cleanup | **Me** (Azure credits) | **Me** (trial limit and expiry) |

What I still own on Railway: the code and its tests, dependency pins, `railway.json`, the variables, the data and its backups, DNS (a wrong CNAME breaks both the site and certificate renewal), watching deploys, logs and spend, and moving off before the trial ends. PaaS takes over the OS, nginx, certbot and systemd. It doesn't take over what the app does or what's in the database.

## Decisions

*(written afterwards, 2026-10-20, in my own words. I didn't keep the in-class versions.)*

### 1. SQLite first, then PostgreSQL

SQLite requires no server and works equally in Codespaces and on the VM. The amount of my site content is dozens of rows written by me. In the VM, the database was a file sitting next to the app, thus no network port required for security.
However, Railway rebuilds the whole container on each deploy, hence a SQLite file disappears, and I have to put it into Railway volume, which can be attached only to one service. Managed Postgres runs as a real DB on Railway's private network as required by the course.

### 2. Azure VM to Railway

I deployed my site with Railway (PaaS), which comes with managed PostgreSQL and GitHub main-branch auto-deploys. Each push to main rebuilds, checks health, and swaps.

Alternatives: Azure VM or other PaaS.

On VM, I managed the OS, Nginx, Certbot for HTTPS, and systemd. There were problems: losing SSH because of changing IPs, downtime after reboot until systemd, pkill ending SSH, and manually pulling git and backing up database when deploying. Railway handles all these things.

In exchange for some loss of control, I get a limited-time trial. The plan allows one custom domain, hence I use Cloudflare to redirect www.zetiantao.me to zetiantao.me.

### 3. Zoho Mail instead of a self-hosted mail server

Zoho Mail Forever Free account for zetian@zetiantao.me. Cloudflare still acts as DNS and I added Zoho MX, SPF, DKIM, DMARC records.

Alternatives: Postfix/Dovecot VM, continue forwarding with Namecheap, or Google Workspace. Forwarding cannot send emails as zetian@zetiantao.me and testing mail did not work until adding MX.

Mail server requires deliverability management, getting a cloud IP without reputation, Azure limitations on students using outbound port 25, and reverse DNS, managing spam, TLS, storage, 24/7 availability, and possible bounce emails when VM crashes. Zoho email is separate from web host, thus the change of hosting does not impact emails.

The free plan provides 5 GB limit and usage of Zoho web/mobile apps only (no IMAP). I use Zoho for emails.

### 4. Removing /admin

On Oct 10, I noticed the live Railway version has no admin password variables set, hence /admin uses default password in the code. Instead of adding secrets and a password protection, I decided to remove the admin editor since I am the only one editing.
Now, I edit the content directly in production: I use railway connect Postgres to access psql and edit the database with SQL.

## Investigated failures

| # | Failure | Kind | Record |
|---|---|---|---|
| 1 | Migrated database was empty on the VM; the site showed "Demo Candidate" and a misleading "database unavailable" banner | Application/database, **real** (Azure migration, 2026-09-29) | [ex03 §3](docs/evidence/ex03.md#3-what-went-wrong-how-i-investigated-and-what-confirmed-the-fix): symptom, SHA-256 comparison of three copies, 0 rows in every table, filled in the real data, re-check showed my name from the DB |
| 2 | Database outage gave HTTP 500 instead of a degraded page | Application/database dependency, **real** (found 2026-10-10, fixed 2026-10-20) | [db-outage-check.md](docs/evidence/db-outage-check.md): `pg_ctl stop -m fast`, traced to unguarded repository calls, fix, tests that failed before and pass after, real Postgres stop/start with timestamps |
| 3 | Stale A record sent the domain to the old VM, so TLS failed with a name mismatch (curl error 60) | DNS/TLS, **deliberate lab failure** (Exercise 05; the output came from the handout, not my system) | [ex05](docs/evidence/ex05.md): prediction, `dig` + `curl -v`, DNS-first diagnosis, CNAME fix, repeated check |
| 4 | SSH and the tunnel timed out after my laptop's network changed | Network, **real** (2026-09-29) | [Azure log](docs/superpowers/plans/2026-09-24-azure-vm-migration.md#progress-log): NSG allowed only the old `/32`; updated `Allow-SSH-Laptop`, re-tested SSH and all pages 200 |
| 5 | 502 from nginx for about 1 s after a reboot | Service ordering, **real**, accepted | [Restart check](docs/superpowers/plans/2026-10-01-operate-the-vm.md#restart-check): nginx was up before the uvicorn workers; cleared by itself |

## Costs, expiry and cleanup

Checked 2026-10-20.

| Service | What it is | Cost so far | Expiry / renewal | Cleanup plan |
|---|---|---|---|---|
| Railway (trial) | Compute (web service) + Postgres with a retained volume | **$0.9023** for the billing period 2026-10-06 to 2026-10-20 (`railway usage`); estimate $0.9147 | Trial ends after 30 days or $5, whichever comes first. The Railway API (`railway api`, workspace `customer` fields, 2026-10-21 00:46 UTC) reports `isTrialing: true`, `trialDaysRemaining: 16`, `creditBalance: 5`, plan `HOBBY`. So the trial ends about **2026-11-06**, unless $5 is used first; $0.90 had been used. | Move to AWS after the midterm and before the trial ends. Then take a final `pg_dump` and delete the `incredible-truth` project (the volume holds the data). |
| Azure for Students | VM `Standard_B2ats_v2` (compute), OS managed disk (storage), Standard static public IP, NSG/VNet/NIC (free) | Compute about $0.0094/h while running (Retail Prices API, [ex03](docs/evidence/ex03.md)). **None since 2026-10-13** (deallocated). The disk and static IP keep billing while stopped. Dollar totals aren't available from the CLI for this subscription. *Credit balance unverified.* | Student credit / subscription term: *unverified* | Keep until the instructor's cleanup directions. Then `az group delete -n rg-career-platform` (removes the disk and IP; can't be undone). The `www` record can stay, since the redirect doesn't need an origin, or be pointed at a placeholder. |
| Namecheap | Domain `zetiantao.me` | *Price not recorded* | Registered 2026-10-05, **expires 2027-10-05** (WHOIS) | Decide on renewal before 2027-10. Turn off auto-renew if it's not needed. |
| Cloudflare | DNS, `www` redirect, edge certificate | Free plan | — | Keep |
| Zoho Mail | `zetian@zetiantao.me` | Forever Free (5 GB) | — | Keep. If the domain lapses, remove the account first. |
| Google Analytics 4 | Property `G-3XLF72EHQC` | Free | Data retention 2 months | Keep |
| GitHub | Public repo | Free | — | Keep |

## Limitations

- The Azure VM is deallocated, against the assignment's "keep it running" (my choice, see above).
- `/healthz` doesn't check the database, so Railway doesn't notice a database outage. That's on purpose, to keep the profile up, but nothing alerts me either.
- Production Postgres has no scheduled backups. Dumps are manual and taken before edits.
- The fallback snapshot only covers the core profile and is refreshed by hand.
- The migration rollback to Azure hasn't been rehearsed.
- DMARC is `p=none` (monitor only), and no aggregate report has been reviewed yet.
- `railway.json` must be migrated to `.railway/railway.ts` before 2026-12-01.
- `career_platform.db` (empty) is still tracked in git and could mislead. `PRODUCT.md` still describes the VM and the admin area.
- The Railway trial end date comes from `trialDaysRemaining` (16 on 2026-10-21), so it could be off by a day depending on when Railway counts the day.

## Reflection

In September, I had never deployed anything before, and I did not have a clue how to proceed. I did not have a GitHub account, and I did not know how to use Visual Studio Code effectively. Throughout this project, I got familiar with how various platforms interact with each other and learned how to use IaaS and PaaS solutions. At first, designing and developing a website seemed like a daunting task. Thanks to agentic coding, I found that designing and developing can be quite easy, but I still need to know how it works and audit the agent's actions.

The problem that helped me the most was the simulated problem from Exercise 5. It got me familiar with the vocabulary of the system and helped me understand the process behind this project. In particular, I learned what DNS and TLS are and how to diagnose a problem with them, which gave me an excellent basis for the rest of the project.

Even though AI was a great help in the project, if I had more time, I would want to understand how the website is developed and coded, so that I could solve some problems in the code myself. Being able to solve problems with code is crucial for my future career.

## Docs and records

- [docs/project-1-submission.md](docs/project-1-submission.md): the Project 1 submission index
- Spec and plans: [spec](docs/superpowers/specs/personal-career-platform.md), [build plan](docs/superpowers/plans/2026-09-15-personal-career-platform.md), [Azure migration](docs/superpowers/plans/2026-09-24-azure-vm-migration.md), [operate the VM](docs/superpowers/plans/2026-10-01-operate-the-vm.md), [Railway migration](docs/superpowers/plans/2026-10-08-railway-postgres-migration.md), [Railway implementation](docs/superpowers/plans/2026-10-08-railway-postgres-implementation.md)
- [docs/how-this-site-is-secured.md](docs/how-this-site-is-secured.md): my HTTPS explanation (Exercise 04, written for the Azure VM)
- [docs/evidence/](docs/evidence/): ex03, ex05, ex06, the Zoho header check, the DB outage check, DNS before Zoho; screenshots in `docs/evidence/img/`
