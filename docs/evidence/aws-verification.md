# AWS deployment verification (guide section 7)

2026-11-01, run from my laptop and over SSH as `ubuntu` on `i-01ab553c3bd48aec2`. Target: https://aws.zetiantao.me (Cloudflare A record, DNS only → 34.201.6.53). Production `zetiantao.me` was still on Railway during these checks.

| Check | Result | Evidence |
|---|---|---|
| Deployed commit | **Pass** | `/opt/career-platform` at `d79c0aa`, the same commit as Railway's `main` |
| Data matches the backup | **Pass** | All 9 tables hashed (UTC, rows sorted with `COLLATE "C"`) on RDS. Identical to `career-railway-20261031T212002Z.source-hashes.txt` |
| Target-only record survives an app restart | **Pass** | Inserted skill id 27 `AWS-TARGET-ONLY test record`, state `draft` (never shown publicly; `/resume` contains 0 matches). Present after `systemctl restart career-platform` and after the reboot. **Deleted before cutover** (section 8) |
| Reboot | **Pass** | `systemctl reboot` at 01:44 UTC. Boot time changed 00:14:28 → 01:45:08. `career-platform` and `nginx` active with no manual steps, the DB connection works with `ssl=true`, 0 error lines in the app journal since boot. The public IP stayed 34.201.6.53 (reboot, not stop/start) |
| Pages | **Pass** | Over HTTPS: `/`, `/resume`, `/portfolio`, both `/portfolio/<slug>`, `/contact`, `/privacy` all 200. `/nope` 404 |
| Assets | **Pass** | `site.css`, `analytics.js` and the Manrope `.woff2` all 200 |
| Redirects | **Pass** | `http://aws.zetiantao.me/portfolio` 301 → `https://aws.zetiantao.me/portfolio` |
| Integrations | **Pass** | GA tag `G-3XLF72EHQC` is in the page. It loads in the browser; the server makes no outbound calls |
| Uploads | **N/A** | The app has no upload route, and `media_asset` has 0 rows |
| HTTPS and renewal | **Pass** | Let's Encrypt YE2, `CN=aws.zetiantao.me`, valid to 2027-01-30. `certbot.timer` active and `certbot renew --dry-run` succeeded |
| Same output as production | **Pass** | `diff` of `/resume` HTML between https://zetiantao.me and https://aws.zetiantao.me: identical |
| SSH restricted | **Pass** | `career-web` port 22 only from `184.81.59.2/32`. `sshd -T`: `passwordauthentication no`, `kbdinteractiveauthentication no`, `permitrootlogin prohibit-password`. A password-only attempt was denied `(publickey)` |
| App port private | **Pass** | uvicorn listens on `127.0.0.1:8000` only. The laptop can't reach `:8000` |
| RDS private | **Pass** | `PubliclyAccessible=False`, the only SG is `career-db`, whose only ingress is 5432 from `sg-04b446403ba8a13eb`. The endpoint resolves to private 172.31.6.108. Laptop `nc` to 5432 timed out |
| RDS settings | **Pass** | Single-AZ, encrypted, 7-day backups, latest restorable time 2026-11-01 01:40:55 UTC |
| IMDSv2 | **Pass** | A metadata request without a token returns 401 |
| Actual costs | **Not verified** | `isba-student` can't read Cost Explorer, Budgets or Free Tier. The estimate is ≈ $34.09/month (plan step 1.2). To check: owner console → Billing → Credits and Bills |

## Production cutover (2026-11-05)

| Check | Result | Evidence |
|---|---|---|
| Data before the switch | **Pass** | Railway dump `career-railway-20261105T213641Z-final.dump` (sha256 `f6402303…`) hashes identical to RDS in all 9 tables |
| DNS change | **Pass** | 21:40:43 UTC apex `CNAME xuwtdiji.up.railway.app` → `A 184.194.107.156`, DNS only. 11 records; only the apex changed; MX `mx/mx2/mx3.zoho.com` unchanged |
| Resolution | **Pass** | `bailey`/`rudy.ns.cloudflare.com`, 1.1.1.1 and 8.8.8.8 all return 184.194.107.156 |
| Pages | **Pass** | `/`, `/resume`, `/portfolio`, both project pages, `/contact`, `/privacy`, `/healthz`, `site.css`, `analytics.js` all 200 from 184.194.107.156, `server: nginx`, real resume content, no degraded banner; `/nope` 404 |
| Redirects | **Pass** | `http://zetiantao.me/resume` and `https://www.zetiantao.me/resume` both 301 → `https://zetiantao.me/resume` |
| Certificate | **Pass** | `CN=zetiantao.me`, Let's Encrypt YE2, valid to 2027-01-30. `certbot renew --dry-run` succeeds for `zetiantao.me` (webroot) and `aws.zetiantao.me` |
