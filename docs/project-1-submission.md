# Project 1 submission: Own Your Corner of the Internet

- **Live site:** https://zetiantao.me
- **Repository:** https://github.com/Zetian1212/career-platform
- **Final commit:** *to be filled in at submission* (`git rev-parse HEAD` on `main`)
- **Name / email:** Zetian Tao, zetian@zetiantao.me

Every link below points to a file, README section or commit in this repository. Anything not verified is marked in the linked record.

## 1. README, spec and plans

- [README](../README.md)
- Original spec: [specs/personal-career-platform.md](superpowers/specs/personal-career-platform.md)
- Original build plan: [plans/2026-09-15-personal-career-platform.md](superpowers/plans/2026-09-15-personal-career-platform.md) (commit `b610eb2`, built in `a813b76`)
- Azure plans: [2026-09-24-azure-vm-migration.md](superpowers/plans/2026-09-24-azure-vm-migration.md), [2026-10-01-operate-the-vm.md](superpowers/plans/2026-10-01-operate-the-vm.md)
- Railway plans (spec + implementation from the Railway lesson): [2026-10-08-railway-postgres-migration.md](superpowers/plans/2026-10-08-railway-postgres-migration.md), [2026-10-08-railway-postgres-implementation.md](superpowers/plans/2026-10-08-railway-postgres-implementation.md)

## 2. Diagrams (Azure, Railway, email, analytics)

- [README → Architecture](../README.md#architecture): the Railway and Azure request paths with locations, protocols and ports, the [email path](../README.md#email-path) and the [analytics path](../README.md#analytics-path)

## 3. Migration: plan, data comparison, cutover, rollback

- Plan written before changing the deployment, with its dependency inventory: [migration plan](superpowers/plans/2026-10-08-railway-postgres-migration.md) ("What has to change, and why", Steps, Risks)
- PostgreSQL compatibility changes: commit `8557f28`; [README → The Railway migration](../README.md#the-railway-migration)
- Real change to the original data (2026-10-07, on the VM, before the copy): [operate-the-VM log](superpowers/plans/2026-10-01-operate-the-vm.md#progress-log)
- Source/target comparison (row counts + every row and column, 2026-10-08 and 2026-10-10: MATCH): [migration plan → Progress log](superpowers/plans/2026-10-08-railway-postgres-migration.md#progress-log)
- Cutover and post-cutover checks (2026-10-10): same log; summary in [README → The Railway migration](../README.md#the-railway-migration)
- Rollback, including data written after cutover: [README → Rolling back](../README.md#rolling-back)
- Who manages what on Azure vs Railway: [README → Who manages what](../README.md#the-railway-migration)

## 4. Azure HTTP/restart evidence and final DNS/HTTPS

- VM facts and the site on the public IP: [ex03](evidence/ex03.md)
- systemd, nginx, NSG rules, SSH, public/private IPs, controlled reboot and crash tests (2026-10-05): [operate-the-VM plan → Restart check and Record](superpowers/plans/2026-10-01-operate-the-vm.md#restart-check)
- Azure HTTPS, certificate and renewal (my Exercise 04 explanation): [how-this-site-is-secured.md](how-this-site-is-secured.md)
- Summary and the VM's current (deallocated) state: [README → The Azure deployment](../README.md#the-azure-deployment)
- Final DNS records, `www` redirect rule, and `dig`/`curl`/`openssl` checks of the apex and `www` over http and https (2026-10-20): [README → Domain and HTTPS](../README.md#domain-and-https)

## 5. Reviewed change through Railway

- [README → A reviewed change through Railway](../README.md#a-reviewed-change-through-railway): the database-outage fix, its review and local verification ([db-outage-check.md](evidence/db-outage-check.md)), then its commit SHA, Railway deployment ID and live result
- Earlier example: `630fbfe` → Railway deployment `685e06f6` (2026-10-17)
- Recovering a previous version (code and data): [README → Rolling back](../README.md#rolling-back)

## 6. Zoho email

- Delivery tests: before-MX bounce, inbound, reply, new outbound: [ex06.md](evidence/ex06.md)
- MX/SPF/DKIM/DMARC records and header analysis: [zoho-header-check.md](evidence/zoho-header-check.md)
- DNS before the switch: [dns-before-zoho.md](evidence/dns-before-zoho.md)
- Summary: [README → Email](../README.md#email)

## 7. GA4

- Screenshots (page_view and outbound click with `link_domain`/`link_url`/`outbound`): [ex06.md §3](evidence/ex06.md#3-google-analytics)
- Action, event, why it's useful, and how collection works: [README → Analytics and privacy](../README.md#analytics-and-privacy)

## 8. Failures, decisions, reflection, costs, limitations

- [Investigated failures](../README.md#investigated-failures): ex03 (application/database, real), [db-outage-check.md](evidence/db-outage-check.md) (database dependency, real), ex05 (DNS/TLS, deliberate lab), SSH/NSG (network, real)
- [Decisions](../README.md#decisions): SQLite → PostgreSQL, VM → Railway, managed vs self-hosted email, removing `/admin`
- [Reflection](../README.md#reflection)
- [Costs, expiry and cleanup](../README.md#costs-expiry-and-cleanup)
- [Limitations](../README.md#limitations)
