# AWS EC2 + Single-AZ RDS Migration Plan

**Goal:** Run the career platform on one EC2 instance (Nginx → uvicorn) with its data in a private Single-AZ RDS PostgreSQL database. The data must match Railway's. Railway keeps serving `zetiantao.me` until every check in section 7 passes.

**Status:** **Rolled back to Railway at 2026-11-01 02:00:35 UTC** (by me, via `!`), about 4.5 minutes after the 01:56 cutover. AWS stays deployed and verified (EIP, both certificates, data identical). Waiting on my decision whether and when to cut over again.

**Deadline:** the Railway trial ends about **2026-11-06** (README "Costs"). Cutover, or a decision to pay for Railway, has to happen before then.

## Source (inspected 2026-10-31)

| | |
|---|---|
| Live site | Railway `incredible-truth` / `production`, web service deploys **`main`** (from 2026-10-17). Apex `zetiantao.me` is a CNAME to Railway (DNS only). `www` is proxied, with a Cloudflare redirect rule to the apex |
| Live data | Railway Postgres **18.6**. Backup `~/backups/career-railway-20261031T212002Z.dump` (pg_dump 18.6, custom format) was restore-tested on 2026-10-31. See `docs/evidence/aws-backup-restore.md` |
| Uploads | None. There's no upload route, `media_asset` has 0 rows, and `app/static` is in Git |
| Stack | FastAPI, SQLAlchemy 2 (`create_all`, no Alembic), psycopg 3, Jinja2, Python 3.12 (`.python-version`), uv. All routes are GET. The server makes no outbound calls (GA runs in the browser) |
| Repo | `github.com/Zetian1212/career-platform` is **public**, so the instance can `git clone` over HTTPS without credentials |

## AWS account (read-only check as `isba-student`, 2026-10-31)

| | |
|---|---|
| Identity | `arn:aws:iam::877481353042:user/isba-student`, profile `isba-4775`, region `us-east-1` |
| Default VPC | `vpc-07407f01af6373f63` (`172.31.0.0/16`), default subnets in 1a–1f, all with public IP on launch |
| Existing | No instances, key pairs or Elastic IPs. Only the `default` security group. RDS reads were denied because the deployment policy isn't attached yet |
| AMI | Ubuntu 26.04 LTS `ami-0bfc5cae5711ffac8` (`ubuntu-resolute-26.04-amd64-server-20261028`, Free Tier eligible). Re-check for a newer build at launch |
| Instance types | `t3.small` (2 GiB) and `t3.micro` (1 GiB), both Free Tier eligible |

**Why Ubuntu 26.04 rather than 24.04:** the restore must use `pg_restore` ≥ 18 because the dump came from pg_dump 18. 26.04's own repository ships PostgreSQL 18 client tools. On 24.04 we'd have to add the PGDG apt repository. Python 3.12 comes from `uv python install 3.12`, whichever Ubuntu we use.

## What has to change, and why

The app needs **no Python changes**. Everything is configuration and new files in `deploy/aws/`:

1. **Database URL and TLS to RDS.** RDS PostgreSQL 15+ has `rds.force_ssl=1`, so connections must use TLS. Set `DATABASE_URL=postgresql+psycopg://career_app:…@<endpoint>:5432/career?sslmode=verify-full&sslrootcert=/etc/ssl/rds/global-bundle.pem` so the client also checks that it's talking to the real RDS host. `app/config.py` already passes `postgresql+psycopg://` URLs through unchanged.
2. **Bind privately, behind Nginx.** uvicorn runs on `127.0.0.1:8000` with `--proxy-headers --forwarded-allow-ips=127.0.0.1`. Nginx is the only public listener (80/443). This is the Azure VM setup from `2026-10-01-operate-the-vm.md`.
3. **Restore before the first start.** `create_app()` runs `create_all` in each worker. If the app starts against an empty database, it creates empty tables, and `pg_restore` then fails with "already exists". So restore first and start the service after. Once the tables exist, `create_all` is a no-op.
4. **Secrets outside Git.** `/etc/career-platform/env` (owned by root, group `career`, mode 640) is loaded by systemd's `EnvironmentFile=`. It holds only `DATABASE_URL`. The RDS master password is used once during setup and isn't stored on the instance.
5. **`railway.json` stays.** Railway still needs it until cutover, and `tests/test_deployment_contract.py` checks it.

New files on this branch: `deploy/aws/career-platform.service`, `deploy/aws/nginx-career-platform.conf`, `deploy/aws/env.example` (names only, no values), and this plan.

## Target architecture

```
Browser ─HTTPS─▶ Cloudflare DNS (test: aws.zetiantao.me, DNS only)
        ─443─▶ EC2 t3.small, sg career-web (Elastic IP before cutover)
                 Nginx :80/:443 (Let's Encrypt cert) ─▶ uvicorn 127.0.0.1:8000, user career, systemd
                 ─5432 TLS, SG-to-SG─▶ RDS PostgreSQL 18, db.t4g.micro, Single-AZ, not public, sg career-db
Admin: SSH :22 from my IP only, key ~/.ssh/isba4775_aws
Backups: RDS automated (7 days) + my pg_dump exports outside AWS
```

## Decisions to confirm before creating anything

| # | Decision | Proposal |
|---|---|---|
| D1 | Instance size | `t3.small`, Standard CPU credits. `t3.micro` (1 GiB) would work but is tight while `uv sync` runs. |
| D2 | Database class | `db.t4g.micro` (Graviton, cheaper than `db.t3.micro`), PostgreSQL **18.x**, the newest minor version RDS offers. Check with `aws rds describe-db-engine-versions` once the policy is attached. |
| D3 | SSH key | A new ed25519 key `~/.ssh/isba4775_aws`, imported with `ImportKeyPair`. Don't reuse the Azure key. |
| D4 | Database users | Master `career_admin` (used for setup only). App role `career_app` owns database `career`, so the restore with `--no-owner` makes `career_app` own every table. |
| D5 | Test hostname | `aws.zetiantao.me`: an A record to the instance, **DNS only**, certificate from certbot over HTTP-01. Mail records and the apex stay unchanged. |
| D6 | Production certificate | DNS-01 through `certbot-dns-cloudflare`, with a Cloudflare token scoped to *Zone:DNS:Edit on zetiantao.me only*, stored root-only (600) on the instance. The certificate is issued before the apex moves. |
| D7 | Stable address | Allocate and associate an Elastic IP before the apex points at AWS. It costs the same as the auto-assigned public IPv4 while attached. |

## Steps

Each step has **Run**, **Check** and **Undo**. Ticks and dated log entries go in as work happens.

### 1. Budget, policy, cost (no resources)

- [ ] **1.1 Zero-spend budget** (owner console, guide section 1). **Check:** the budget is listed under Budgets.
- [x] **1.2 Cost estimate** (2026-10-31). Prices are from AWS's public price-list files for us-east-1 (EC2 and RDS published 2026-10-29, VPC 2026-10-16, Data Transfer 2026-09-16). The Pricing, Budgets and Free Tier APIs are denied to `isba-student`. One month is 730 hours.

  | Item | Rate | Month |
  |---|---|---|
  | EC2 t3.small, Linux, On-Demand | $0.0208/h | $15.18 |
  | EBS gp3 root, 16 GB (baseline 3000 IOPS / 125 MB/s included) | $0.08/GB-mo | $1.28 |
  | Public IPv4, 1 address (an Elastic IP in use costs the same) | $0.005/h | $3.65 |
  | RDS db.t4g.micro, PostgreSQL, Single-AZ | $0.016/h | $11.68 |
  | RDS gp3 storage, 20 GB | $0.115/GB-mo | $2.30 |
  | RDS backups (free up to 20 GB, the provisioned size; the DB is about 10 MB) | $0.095/GB-mo beyond that | $0.00 |
  | Data out to the internet (the first 100 GB/month across the account are free; this site uses well under 1 GB) | $0.09/GB beyond that | $0.00 |
  | EC2↔RDS (same AZ, so no transfer charge; it would be $0.01/GB across AZs) | — | $0.00 |
  | **Total** | | **≈ $34.09/month (≈ $1.12/day)** |

  $100 of credits covers about **2.9 months**. Running 2026-11-01 to mid-December (45 days) costs about **$50**. Ways to save: `t3.micro` (−$7.59) or `db.t4g.micro` instead of `db.t3.micro` (already chosen, saves $1.46). Standard CPU credits mean there are no T3 surplus charges.
- [x] **1.3 Review the `ISBA4775EC2Migration` policy** (attached by the owner on 2026-10-31. Checked: `describe-db-instances` returns 0 instead of AccessDenied. RDS offers PostgreSQL 18.1–18.4 and **18.6** on `db.t4g.micro` with gp3, so D2 = **18.6**, the same as Railway) (fetched 2026-10-31). It allows EC2 and RDS create, modify and delete in us-east-1 on `*`, including resources unrelated to this project. It denies instance types other than t3.micro/small, launches without IMDSv2, DB classes other than t3/t4g.micro, Multi-AZ, storage over 20 GB and unencrypted databases. It doesn't enforce cost. The account has no other work, so no narrowing is needed. The owner attaches it.
  **Reviewed 2026-10-31.** The statements cover everything steps 2–4 and 9 need. Gaps it doesn't guard, which the plan handles by how each call is made: EBS volume size and type, AMI choice (paid Marketplace AMIs), number of instances and Elastic IPs, security-group CIDRs (e.g. 5432 to the world), RDS `PubliclyAccessible`, storage autoscaling, and encryption when the flag is omitted. It grants no cost visibility (`ce:*`, `budgets:*`, `freetier:*`), so cost checks happen in the owner console.
  **Check:** `aws rds describe-db-instances --profile isba-4775` now returns an empty list instead of AccessDenied.

### 2. Network and access (EC2)

- [x] **2.1 Key:** (done 2026-10-31: `career-aws`, `key-075df6798cf325454`, fingerprint `SHA256:Wz7TM7MX…pAEw`, no passphrase, file mode 600) `ssh-keygen -t ed25519 -f ~/.ssh/isba4775_aws`, then `aws ec2 import-key-pair --key-name career-aws --public-key-material fileb://~/.ssh/isba4775_aws.pub`. **Undo:** `delete-key-pair`.
- [x] **2.2 `career-web` SG:** (`sg-04b446403ba8a13eb`. 22 from `184.81.59.2/32`, the laptop's IP on 2026-10-31. Update the rule if that IP changes) inbound 22/tcp from `<my IP>/32`, 80 and 443/tcp from `0.0.0.0/0`. Default outbound. **Check:** `describe-security-groups` shows exactly three ingress rules.
- [x] **2.3 `career-db` SG:** (`sg-06fcb589bdcc3b9f4`, single rule 5432 from `sg-04b446403ba8a13eb`) inbound 5432/tcp **only from `career-web`** (a group reference, no CIDR). **Check:** there's no `0.0.0.0/0` rule.

### 3. EC2 instance

- [x] **3.1 Launch once:** (`i-01ab553c3bd48aec2`, launched 2026-11-01 00:13 UTC with client token `career-platform-launch-20261031`. Public IP **34.201.6.53** (auto-assigned, changes on stop/start), private `172.31.2.216`, us-east-1a, IMDSv2 required, Standard credits, root `vol-0b572c7d521d42c1f` 16 GB gp3 encrypted, 3000 IOPS / 125 MB/s) the 26.04 AMI, `t3.small`, `--credit-specification CpuCredits=standard`, a 16 GB **encrypted gp3** root volume, `HttpTokens=required` (IMDSv2), key `career-aws`, SG `career-web`, a default subnet in **us-east-1a**, tag `Name=career-platform`.
  **Check:** in the console and with `describe-instances`, confirm the ID, public IP, SG, volume encrypted, IMDSv2 required and Standard credits.
  **Undo:** `terminate-instances`. The root volume is deleted with it.
- [x] **3.2 First SSH:** (ED25519 host key `SHA256:7cQ1V9d+4aZSJcXqF9NRj1gxs00PCkxTkRMLCTNpYz8` from `get-console-output` matched `ssh-keyscan`, then added to known_hosts. `ssh -i ~/.ssh/isba4775_aws ubuntu@34.201.6.53` gives Ubuntu 26.04.1 LTS) get the host key fingerprint from `get-console-output` and compare it with the fingerprint ssh shows before accepting. **Check:** `ubuntu@` login works.

### 4. RDS database

- [x] **4.1 Create once:** (2026-11-01. `career-platform-db`, endpoint `career-platform-db.ccr6woqeij3z.us-east-1.rds.amazonaws.com:5432`, private IP 172.31.6.108, subnet group `default`. All settings verified with `describe-db-instances`. The master password is in the macOS Keychain as service `career-platform-rds`, account `career_admin`. It went to AWS through a 600 temp file that was deleted afterwards, and was never printed) `career-platform-db`, PostgreSQL 18.x, `db.t4g.micro`, `--no-multi-az`, `--availability-zone us-east-1a` (same zone as EC2, so no cross-AZ transfer), 20 GB gp3 **encrypted**, no max-allocated-storage (autoscaling off), `--no-publicly-accessible`, SG `career-db`, master `career_admin` with a generated password piped in, never printed, backup retention 7, **`--storage-encrypted` passed explicitly** (the policy's encryption deny only fires when the request says `false`), `--max-allocated-storage` left unset (the policy doesn't cap autoscaling), `--no-deletion-protection` (the policy's `StringNotEqualsIfExists` class rule may deny any `ModifyDBInstance` that doesn't name a class, so we might not be able to turn protection off again), tag `Name=career-platform`.
  **Check:** in the console, endpoint, class, Single-AZ, **Publicly accessible: No**, encryption on, backups 7 days.
  **Undo:** `delete-db-instance --final-db-snapshot-identifier career-final-<date>`.
- [x] **4.2 Prove it's private:** (2026-11-01. The endpoint resolves to private 172.31.6.108. Laptop `nc` timed out. EC2 TCP connect succeeded) from the laptop, `nc -z <endpoint> 5432` must fail. From EC2, it succeeds.

### 5. Server setup (on EC2, while RDS is creating)

- [x] **5.1 Packages:** (nginx 1.28.3, pg_restore/psql 18.6, certbot 4.0.0, git 2.53.0, uv 0.13.6 in /usr/local/bin. No reboot required after the upgrade) `apt update && apt upgrade`, then `nginx`, `postgresql-client-18`, `certbot`, `python3-certbot-nginx`, `git`. Install uv. **Check:** `pg_restore --version` shows 18.x.
- [x] **5.2 App user and code:** (user `career`, home /var/lib/career, nologin. `/opt/career-platform` at **`d79c0aa`**, the same as Railway's `main`. Python 3.12.16 in /var/lib/career/python. `uv sync --frozen`) system user `career` with no login shell. `git clone` into `/opt/career-platform`, check out the **exact commit** to deploy and record its SHA. Run `uv python install 3.12` and `uv sync --frozen --no-dev` as `career`.
- [x] **5.3 RDS CA bundle:** (114 certificates) download `https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem` to `/etc/ssl/rds/`.

### 6. Database restore and service

- [x] **6.1 Copy the dump to EC2** (2026-11-01. SHA-256 matched. The server copy was removed with `shred -u` after 6.3. The source-hash file stays in ~/restore) with `scp` to `/home/ubuntu/restore/`, mode 600. Check the SHA-256 matches `fa821306…3632426`.
- [x] **6.2 Roles:** (`career_app` created, `GRANT career_app TO career_admin` (PG16+ needs it for `CREATE DATABASE … OWNER`), and `career` owned by `career_app`. The app password is generated on the server and lives only in `/etc/career-platform/env` (root:career 640). Connection checked: `ssl=t` with verify-full) as `career_admin`, `CREATE ROLE career_app LOGIN PASSWORD …` (generated and written straight into `/etc/career-platform/env`, never echoed), then `CREATE DATABASE career OWNER career_app`.
- [x] **6.3 Restore** (0.21 s into an empty DB (0 tables before). **All 9 table hashes identical to Railway.** All tables owned by `career_app`, sequences at max(id)) as `career_app`: `pg_restore --no-owner --no-privileges --exit-on-error -d career <dump>`. Record how long it takes.
  **Check:** the 9 table hashes (UTC, `COLLATE "C"`, the method in the evidence doc) match `career-railway-20261031T212002Z.source-hashes.txt`, and the sequences are at `max(id)`.
- [x] **6.4 systemd unit** (installed from `deploy/aws/`, enabled, running as `career`: manager plus 2 workers on 127.0.0.1:8000. `/healthz` ok) (`deploy/aws/career-platform.service`): `User=career`, `EnvironmentFile=/etc/career-platform/env`, uvicorn `--host 127.0.0.1 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips=127.0.0.1`, `Restart=on-failure`. Then `enable --now`. **Check:** `curl -s 127.0.0.1:8000/healthz` returns ok, and `ss -ltnp` shows 8000 on 127.0.0.1 only.
- [x] **6.5 Nginx** (site enabled, default removed, `nginx -t` ok, nginx enabled. From the laptop with `Host: aws.zetiantao.me` on 34.201.6.53: every page 200, `/nope` 404, real resume content, no degraded banner, `/resume` HTML **identical** to production. Port 8000 unreachable from outside) (`deploy/aws/nginx-career-platform.conf`): `server_name aws.zetiantao.me`, `proxy_pass http://127.0.0.1:8000` with `Host` and `X-Forwarded-*` headers. Remove the default site. **Check:** `nginx -t` passes, and `curl -H 'Host: aws.zetiantao.me' http://<ip>/` returns 200 with real data.

### 7. Test subdomain and verification (the guide's section 7)

- [x] **7.1 DNS:** (2026-11-01, `cf` CLI: record `0c14be3ca6be47548512c8151d137237`, A `aws` → 34.201.6.53, DNS only, TTL 300. Diff against the before-snapshot: one record added, nothing changed or removed. 1.1.1.1 resolves it. The apex still resolves to Railway 69.46.46.100 (`server: railway-hikari`). Note: `cf --zone zetiantao.me` put the name into the API path, so use the zone ID `a70285b2…`) add an A record `aws` → the instance IP, DNS only. Don't touch the apex, `www`, MX, SPF, DKIM or DMARC. **Undo:** delete the record.
- [x] **7.2 HTTPS:** (2026-11-01. Let's Encrypt YE2 certificate for `aws.zetiantao.me`, valid to 2027-01-30, account email zetian1212@gmail.com. `certbot.timer` active and `renew --dry-run` succeeded. http→https returns 301. The HTTPS pages return 200, `/nope` 404, and `/resume` is identical to production. The repo's `deploy/aws/nginx-career-platform.conf` now matches the live file) `certbot --nginx -d aws.zetiantao.me` with the HTTP→HTTPS redirect. **Check:** `openssl s_client` shows a Let's Encrypt certificate, and `certbot renew --dry-run` passes.
- [x] **7.3 Checks, with evidence in `docs/evidence/aws-verification.md`:** (2026-11-01. All pass except actual costs, which are unverified: no billing access)
  - the deployed SHA matches the intended commit
  - row hashes match the backup
  - a target-only test record survives `systemctl restart`
  - after `sudo reboot`, the app, Nginx and the RDS connection all come back without manual steps
  - `/`, `/resume`, `/portfolio`, both project pages, `/contact`, `/privacy` and `/static/...` return 200, an unknown path returns 404, and http redirects to https
  - SSH is refused from a different IP (or the rule shows only `/32`)
  - RDS is `PubliclyAccessible=false` and its SG ingress references only `career-web`
  - spend so far, from Cost Explorer or the Credits page

### 8. Cutover (only when step 7 is fully green; the guide's section 8)

- [x] 8.1 Elastic IP allocated and associated (D7). Update the `aws` record. (`eipalloc-0a9d6a60e770b02f7`, **184.194.107.156**. The host key at the new IP matches `SHA256:7cQ1V9d…`. `aws` record edited to the EIP. The old auto IP 34.201.6.53 was released)
- [x] 8.2 Production certificate for `zetiantao.me` issued over DNS-01 (D6) before the switch. (**Changed from D6:** no Cloudflare token on the server. `certbot certonly --manual` with hooks `/usr/local/sbin/acme-dns-{auth,cleanup}`; I created the `_acme-challenge` TXT from the laptop with `cf`, confirmed it on both Cloudflare NS, and deleted it after issuance. Certificate valid to 2027-01-30. Nginx site `deploy/aws/nginx-zetiantao.me.conf` installed; through the EIP `/`, `/resume`, `/healthz` return 200 and http returns 301. **After cutover:** switch renewal to `certbot certonly --webroot -w /var/www/letsencrypt -d zetiantao.me --cert-name zetiantao.me --force-renewal --deploy-hook 'systemctl reload nginx'`, because a manual cert can't auto-renew)
- [x] 8.3 Save the current apex record. (Saved: `dc7eeacff665e5b1a617497d823b651a` CNAME `zetiantao.me` → `xuwtdiji.up.railway.app`, DNS only, TTL auto. Test record id 27 deleted and `skill_id_seq` reset to 26. Final dump `~/backups/career-railway-20261101T015126Z-final.dump` (sha256 `d94473b0…`): its hashes are identical to the 10-31 backup **and** to RDS, so no restore was needed. Writes freeze: I don't edit via `railway connect`.) Freeze Railway writes (no `railway connect` edits). Take a final dump, restore it, compare, and delete the target-only test record.
- [x] 8.4 Replace the apex CNAME to Railway with an A record to the Elastic IP (DNS only). Change nothing else.
- [x] 8.5 Verify production over HTTPS. Only then make edits on AWS. (Apex A → 184.194.107.156 at 01:56 UTC, run by me via `!` because the auto-mode classifier blocks the agent. Only 1 of 11 records changed. NS, 1.1.1.1 and 8.8.8.8 agree. All pages 200 from nginx, 404 and 301 correct, `www` → apex 301, MX unchanged. Apex certificate reissued with webroot (`authenticator = webroot`, `renew_hook = systemctl reload nginx`) and the manual DNS hooks removed)

**Rollback:** put the saved apex CNAME back. If anything was written on AWS after cutover, dump those rows and apply them to Railway first, because DNS doesn't move data.

### 9. After

- [ ] README: decision, request path (Mermaid), backup and RPO/RTO, verification, costs, next step.
- [ ] Cleanup schedule: when the course ends, delete the RDS instance with a final snapshot (a stopped RDS instance restarts itself after 7 days), terminate EC2, release the Elastic IP, delete the SGs and key pair. Delete the Railway project after cutover is stable.

## Risks

| Risk | Mitigation |
|---|---|
| Railway trial ends about 2026-11-06, before AWS is ready | Keep the dumps current. If AWS slips, decide by 11-05 whether to pay for Railway Hobby |
| The app starts before the restore and creates empty tables | Step order: 6.3 runs before 6.4. If it happens anyway, use `pg_restore --clean --if-exists` |
| Auto-assigned public IP changes on stop/start | Don't stop the instance before D7. Use an Elastic IP before cutover |
| Credits drain faster than expected | Zero-spend budget plus a weekly look at the Credits page |
| The broad deployment policy could affect other resources | The account holds only this project (checked 2026-10-31) |

## Progress log

- **2026-10-31** Backup taken and restore-tested locally (evidence doc). AWS CLI 2.39.3 installed. `isba-4775` profile signed in as `isba-student`, after an accidental root session was replaced. Read-only account survey done (above). Branch `aws-migration` created from `d79c0aa`. Plan written, nothing created in AWS. Cost estimate from the public price lists: ≈ $34.09/month (step 1.2). The credit balance, expiry and budget couldn't be read as `isba-student` and need checking in the owner console.
- **2026-10-31/11-01** Launch settings approved. Created the key pair, both SGs and instance `i-01ab553c3bd48aec2` (one launch, client token). Every setting verified by `describe-*`. Host key verified against the console output before the first SSH.
- **2026-11-01** RDS created once and verified private. Server packages, app user, code at `d79c0aa` and Python deps installed. Nothing restored or started yet.
- **2026-11-01** Step 6: dump copied (checksum ok), `career_app` and DB created, restored in 0.21 s, all 9 tables identical to Railway. Service and Nginx installed from `deploy/aws/` and enabled. Public-IP page checks pass and `/resume` matches production byte for byte. Production DNS unchanged.
- **2026-11-01** Cloudflare `aws` A record created (DNS only). `http://aws.zetiantao.me/resume` returns 200 from EC2. Production unchanged.
- **2026-11-01** HTTPS on https://aws.zetiantao.me (certbot --nginx, redirect on, renewal dry run ok).
- **2026-11-01** 7.3 verification passed (`docs/evidence/aws-verification.md`), including the reboot. EIP 184.194.107.156 attached. Apex certificate via DNS-01 with a temporary TXT (deleted). Final Railway dump identical to RDS. The apex switch attempt was **blocked by the auto-mode classifier**; nothing changed in DNS. README has the AWS section and the Mermaid diagram, with cutover marked pending.
- **2026-11-01** Cutover: apex switched to the EIP (01:56 UTC), production verified, apex certificate moved to webroot renewal. README updated to "Now: AWS".
- **2026-11-01 02:00 UTC** Apex set back to `CNAME xuwtdiji.up.railway.app` (DNS only) by me. Cloudflare NS, 1.1.1.1 and 8.8.8.8 return 69.46.46.100, and Railway serves 200 (`railway-hikari`). RDS hashes are unchanged since the final Railway dump, so nothing written during the AWS window needs reconciling. The README was then corrected: Railway "Now", AWS "Standby", cutover recorded as a rehearsal plus rollback.
- **2026-11-01** Renewal dry runs: `aws.zetiantao.me` succeeds; `zetiantao.me` fails `unauthorized` while the apex is on Railway (expected, since webroot needs the apex on EC2). Its certificate is valid to 2027-01-30.
