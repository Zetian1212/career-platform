# How this site is secured

**How do I know my data to your site is encrypted?**

The site lives at `https://zetiantao.me` and `https://www.zetiantao.me`. When you open it, your browser first makes the server prove it really is zetiantao.me by showing an ID card called a certificate. Then the two of them agree on a secret code, and everything you send after that is scrambled with it. Anyone in between, like your Wi-Fi or your internet provider, only sees gibberish. If you type the address without `https`, the server sends you to the `https` version anyway, so nothing you send goes out in the clear. Everything below was checked on 2026-10-07 (UTC) on the live server `vm-career-platform` (Azure, North Central US, Ubuntu 24.04).

## 1. The certificate

The certificate is the site's ID card. It was issued by Let's Encrypt and covers both `zetiantao.me` and `www.zetiantao.me`. It uses an ECDSA key, started working on 2026-10-06 at 21:03:50 UTC, and expires on 2027-01-04 at 21:03:49 UTC, which was 88 days away when I checked. This is what `sudo certbot certificates` shows on the server:

```
Certificate Name: zetiantao.me
  Key Type: ECDSA
  Domains: zetiantao.me www.zetiantao.me
  Expiry Date: 2027-01-04 21:03:49+00:00 (VALID: 88 days)
```

Both names point to the server's public IP: `dig +short zetiantao.me www.zetiantao.me` returns `172.183.16.158` twice.

## 2. Renewal

Let's Encrypt certificates expire after 90 days, which means the server has to auto-renew them. There is a job called `certbot.timer`, which calls `certbot renew` twice per day. The job will only renew a certificate if it expires within the next 30 days; otherwise, it will do nothing when executed. If the renewal happens, it relies on the nginx plugin configured in `/etc/letsencrypt/renewal/zetiantao.me.conf`: Let's Encrypt verifies my ownership of the domain by fetching a one-time challenge file from nginx on port 80, then issues the new certificate, and nginx reloads with it. This is why port 80 must be open.

```
$ sudo certbot renew --dry-run
Processing /etc/letsencrypt/renewal/zetiantao.me.conf
Simulating renewal of an existing certificate for zetiantao.me and www.zetiantao.me
Congratulations, all simulated renewals succeeded:
  /etc/letsencrypt/live/zetiantao.me/fullchain.pem (success)
```

```
$ systemctl status certbot.timer
Loaded: loaded (/usr/lib/systemd/system/certbot.timer; enabled; preset: enabled)
Active: active (waiting) since Tue 2026-10-06 21:47:43 UTC; 1 day 1h ago
Trigger: Thu 2026-10-08 05:15:43 UTC; 5h 59min left
```

## 3. Open ports

The Azure firewall only lets traffic through three ports. Port 22 is how I log in to manage the server, and only two specific IP addresses that I use are allowed to reach it. Even from those, it only accepts my SSH key, not a password. Port 80 is open to everyone; it sends visitors over to HTTPS and lets Let's Encrypt check the domain when renewing. Port 443 is open to everyone and is the encrypted website itself.

## 4. Where encryption starts and ends

```
Your browser ══ encrypted (HTTPS, port 443) ══▶ nginx on the server ── plain HTTP ──▶ app at 127.0.0.1:8000
              scrambled over the internet        (unscrambled here)     never leaves the server
```

The browser scrambles the request before it leaves the visitor's device, and it stays scrambled across the internet. On the server, a program called nginx receives it first. nginx holds the certificate and the key, so it unscrambles the request. It then passes the request to the website app, a separate program on the same server. That handoff is not scrambled, but it happens inside the machine, from one program to another, and never goes over any cable or Wi-Fi. The only way to read it would be to have already broken into the server. nginx also tells the app that the visitor arrived over a secure connection, so the app treats the request as HTTPS even though it only ever sees the unscrambled copy.

## 5. Checking the certificate yourself in Chrome

Open `https://zetiantao.me`, click the icon to the left of the address, then click **Connection is secure**, then **Certificate is valid**. Check that **Issued To** says `zetiantao.me`, **Issued By** says Let's Encrypt, and today's date falls inside the **Validity Period**. If Chrome instead says "Not secure" or shows a warning, don't type anything in.

## 6. openssl output

Run from my laptop against the live site:

```
$ echo | openssl s_client -connect zetiantao.me:443 -servername zetiantao.me 2>/dev/null | openssl x509 -noout -subject -issuer -dates
subject=CN=zetiantao.me
issuer=C=US, O=Let's Encrypt, CN=YE2
notBefore=Oct  6 21:03:50 2026 GMT
notAfter=Jan  4 21:03:49 2027 GMT
```
