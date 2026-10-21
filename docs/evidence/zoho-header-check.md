# Zoho Mail header check

This analyses the authentication of mail sent from `zetian@zetiantao.me`. The DNS records were read on 2026-10-20 at 20:25 UTC with `dig` from my laptop and confirmed with the Cloudflare CLI (`cf dns records list --zone zetiantao.me`). The header is from "Ex06 Test03: Outbound", sent from Zoho webmail on 2026-10-17 at 12:13 PT and received by my LMU Microsoft 365 mailbox. The delivery tests themselves are in [ex06.md](ex06.md).

## 1. The records

| Record | Name | Value (as published) | Purpose |
|---|---|---|---|
| MX 10 / 20 / 50 | `zetiantao.me` | `mx.zoho.com`, `mx2.zoho.com`, `mx3.zoho.com` | Tells other mail servers where to deliver mail for `@zetiantao.me`. The lowest number is tried first. Published 2026-10-13 21:35 UTC. They replaced Namecheap's forwarding MX records ([before](dns-before-zoho.md)). |
| TXT (SPF) | `zetiantao.me` | `v=spf1 include:zohomail.com ~all` | Lists which servers may send mail for the domain: Zoho's. `~all` asks receivers to treat other senders as suspicious (soft fail) rather than reject them outright. |
| TXT (DKIM) | `zmail._domainkey.zetiantao.me` | `v=DKIM1; k=rsa; p=MIGfMA0GCSq…` | The public half of the key that Zoho signs outgoing mail with. `zmail` is the selector, so a receiver knows which key to look up. |
| TXT (DMARC) | `_dmarc.zetiantao.me` | `v=DMARC1; p=none; rua=mailto:zetian@zetiantao.me` | Tells receivers what to do when a message fails SPF and DKIM alignment (`p=none`: deliver it, but report) and where to send aggregate reports. |
| TXT | `zetiantao.me` | `zoho-verification=zb33665332.zmverify.zoho.com` | Proved to Zoho that I control the domain. |

All of them are **DNS only**: mail records can't be proxied by Cloudflare.

## 2. The header

```
Authentication-Results: mx.microsoft.com 1; spf=pass (sender IP is
 165.173.180.52) smtp.mailfrom=zetiantao.me; dkim=pass (signature was
 verified) header.d=zetiantao.me;dmarc=pass action=none
 header.from=zetiantao.me;compauth=pass reason=100
```

| Check | Result | What it shows |
|---|---|---|
| SPF | `pass` | The envelope sender's domain (`smtp.mailfrom=zetiantao.me`) publishes an SPF record that includes Zoho, and the sending IP `165.173.180.52` (Zoho's `sender6-of-o52.zoho.com`) is in it. |
| DKIM | `pass` | Microsoft fetched the `zmail` key from DNS and the signature verified, with signing domain `header.d=zetiantao.me`. The signed headers and body weren't changed in transit. |
| DMARC | `pass`, `action=none` | The visible From domain (`header.from=zetiantao.me`) matches the domains that passed SPF and DKIM (alignment). Since it passed, the `p=none` policy never came into play. |
| compauth | `pass` | Microsoft's own combined verdict, so the message wasn't marked as spoofed. |

## 3. What this proves, and what it doesn't

- Mail sent from Zoho at my domain authenticates fully at a major receiver, and the receiver sees `zetian@zetiantao.me` as the sender (ex06 rows Test02 and Test03).
- Incoming mail reaches Zoho through the MX records (ex06 row Test01). The before-MX bounce is in ex06 too.
- **The DMARC report confirms both outgoing test messages passed.** On 2026-10-19 at 15:41 UTC, Zoho received an aggregate report from `dmarcreport@microsoft.com` (submitter `enterprise.protection.outlook.com`, report ID `9aec1283…`). It covers mail Microsoft received from my domain between 2026-10-17 00:00 and 2026-10-18 00:00 UTC. I downloaded the XML attachment and read it on 2026-10-21; it's committed as [dmarc-report-microsoft-2026-10-17.xml](dmarc-report-microsoft-2026-10-17.xml). That proves the `rua` address in the DMARC record works.

  | Source IP | Messages | SPF | DKIM (`zmail`) | Disposition |
  |---|---|---|---|---|
  | `165.173.180.19` | 1 | pass | pass | none |
  | `165.173.180.52` | 1 | pass | pass | none |

  Both rows have `header_from` and `envelope_from` = `zetiantao.me` and `envelope_to` = `lion.lmu.edu`. Two messages fits the two outgoing ex06 tests that day (Test02 reply, Test03 new message). `165.173.180.52` is the IP in the Test03 header above. Matching `165.173.180.19` to Test02 is my inference: the report doesn't say which message came from which IP. Both IPs passed SPF, so `include:zohomail.com` authorises them. There were no failing rows, which means nobody else was sending mail as my domain to Microsoft that day. The report also echoes the published policy: `p=none`, `sp=none`, relaxed alignment (`adkim=r`, `aspf=r`), `pct=100`. `p=none` only monitors. Moving to `p=quarantine` would let receivers act on spoofed mail. One clean day of reports is a start, but I'd want a few weeks of them first.
- The full raw header isn't committed because it contains private routing and mailbox details. Only the `Authentication-Results` line is quoted.
