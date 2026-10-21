# Cloudflare `www` redirect rule

Exported 2026-10-21 at about 00:44 UTC with the Cloudflare CLI (`cf rulesets get 0fac30a128b844209d482c9b5f2ea5eb --zone zetiantao.me`). The rule was last changed 2026-10-20 03:04 UTC. Railway's plan allows one custom domain, which is the bare `zetiantao.me`, so `www` is answered by Cloudflare. The `www` A record is proxied, which lets Cloudflare see the request and send a 301 to the bare domain, keeping the path. The origin behind the record, the Azure VM, is never contacted, which is why this still works while the VM is deallocated.

```json
{
  "description": "",
  "id": "0fac30a128b844209d482c9b5f2ea5eb",
  "kind": "zone",
  "last_updated": "2026-10-20T03:04:31.16856Z",
  "name": "default",
  "phase": "http_request_dynamic_redirect",
  "rules": [
    {
      "action": "redirect",
      "action_parameters": {
        "from_value": {
          "preserve_query_string": false,
          "status_code": 301,
          "target_url": {
            "expression": "wildcard_replace(http.request.full_uri, r\"http*://www.*\", r\"https:///${2}\")"
          }
        }
      },
      "description": "Redirect from WWW to root",
      "enabled": true,
      "expression": "(http.request.full_uri wildcard r\"http*://www.*\")",
      "id": "77fa1219d9bf4a69a06df3415bb65045",
      "last_updated": "2026-10-20T03:04:31.16856Z",
      "ref": "77fa1219d9bf4a69a06df3415bb65045",
      "version": "3"
    }
  ],
  "version": "3"
}
```

- **Matches:** any URL starting with `http://www.` or `https://www.` (`http.request.full_uri wildcard "http*://www.*"`).
- **Sends:** `301` to `https://` plus everything after `www.` (`${2}` is the second wildcard), so `http://www.zetiantao.me/resume` goes to `https://zetiantao.me/resume`.
- **`preserve_query_string: false`** doesn't drop the query here. The wildcard replacement already copies the full URI, query included, as the `?x=1` check shows.

Verification, the same day: `http://www.zetiantao.me/`, `https://www.zetiantao.me/` and `https://www.zetiantao.me/resume?x=1` all return `301` to the matching `https://zetiantao.me/…` URL. The certificate on `www` is Cloudflare's edge certificate for `*.zetiantao.me` (see README → Domain and HTTPS).
