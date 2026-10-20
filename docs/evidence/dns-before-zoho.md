# DNS records before the Zoho Mail switch

This is a snapshot of every DNS record in the `zetiantao.me` Cloudflare zone, taken on October 13, 2026 at 21:10 UTC, before any records were changed for Zoho Mail. It's here so the zone can be restored if the switch goes wrong.

I listed the records with the Cloudflare CLI:

```
cf dns records list --zone zetiantao.me --per-page 100
```

It returned 9 records. None is proxied through Cloudflare, and every TTL is `1`, which means Automatic.

| Type | Name | Priority | Content | Record ID | Last modified (UTC) |
|---|---|---|---|---|---|
| A | www.zetiantao.me | | `172.183.16.158` | `b311b12e2206788c845b212a00c77a1a` | 2026-10-05 19:16 |
| CNAME | zetiantao.me | | `xuwtdiji.up.railway.app` | `dc7eeacff665e5b1a617497d823b651a` | 2026-10-11 00:23 |
| MX | zetiantao.me | 10 | `eforward1.registrar-servers.com` | `2c24208a9225de770a14197491e5eaf9` | 2026-10-05 19:14 |
| MX | zetiantao.me | 10 | `eforward2.registrar-servers.com` | `05bc88162ff20c2c15b949c573422410` | 2026-10-05 19:14 |
| MX | zetiantao.me | 10 | `eforward3.registrar-servers.com` | `8b932e0e508693b8aef78a9f12c857c6` | 2026-10-05 19:14 |
| MX | zetiantao.me | 15 | `eforward4.registrar-servers.com` | `3b6b60d9f83ac82579da651829619a41` | 2026-10-05 19:14 |
| MX | zetiantao.me | 20 | `eforward5.registrar-servers.com` | `c39cc77a7d35cf31ca42b5874499a7fc` | 2026-10-05 19:14 |
| TXT | _railway-verify.zetiantao.me | | `"railway-verify=7253d9d67db4f55f6358c062fb42c2f1fa77eb7125606940af4702c6a09a8429"` | `d0ede55d60d209dc07d40118bd41f972` | 2026-10-11 00:23 |
| TXT | zetiantao.me | | `"v=spf1 include:spf.efwd.registrar-servers.com ~all"` | `14124ed4cc84552d2fd0cace01870600` | 2026-10-05 19:14 |

## What each record does

- **A `www`**: sends `www.zetiantao.me` to the Azure VM.
- **CNAME apex**: sends `zetiantao.me` to the app on Railway. Cloudflare flattens a CNAME at the apex, which is why it can sit alongside the MX and TXT records there.
- **MX `eforward1`–`5`**: deliver mail for the domain to Namecheap's email forwarding.
- **TXT `_railway-verify`**: proves to Railway that I own the domain.
- **TXT SPF**: allows Namecheap's forwarding servers to send mail for the domain.

The Zoho switch will replace the five MX records and the SPF record. The A, CNAME and Railway verification records shouldn't be touched.
