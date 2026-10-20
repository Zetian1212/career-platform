# Request path diagrams: entering zetiantao.me in a browser

Midterm study diagrams. Step numbers 0–10 match the step table:
0 network join, 1 parse URL, 2 DNS, 3 leaving the house, 4 TCP, 5 TLS, 6 redirect, 7 edge to app, 8 app to database, 9 response, 10 rest of the page.

**Assumed setting: my home network.** A typical home setup is assumed, not checked against my actual router: one home router (often combined with the ISP's modem) does Wi-Fi, switching, routing, DHCP, DNS forwarding, NAT and firewall. Its DHCP gives the laptop a private address, with the router itself as both the gateway and the DNS server. The router forwards DNS queries to the ISP's recursive resolver. To check at home: `ipconfig getifaddr en0` (laptop address), `route -n get default` (gateway), `scutil --dns | grep nameserver` (DNS server).

## 1. Where everything sits (hardware, services, and the Railway host)

```mermaid
flowchart LR
  subgraph HOME["My home network (private addresses, e.g. 192.168.x.x)"]
    LAPTOP["Laptop<br/>browser + OS<br/>Wi-Fi card<br/>private address from DHCP"]
    ROUTER["Home router<br/>Wi-Fi access point + switch<br/>gateway + DHCP + DNS forwarder<br/>NAT + firewall"]
    MODEM["Modem / ONT<br/>(may be built into the router)"]
  end

  ISP["ISP network<br/>gives the router its one public address"]
  NET["Internet routers"]

  subgraph DNS["DNS (separate exchange)"]
    RES["ISP recursive resolver"]
    ROOT["Root servers"]
    TLD[".me TLD servers"]
    CF["Cloudflare<br/>authoritative DNS<br/>flattened CNAME"]
  end

  subgraph RAILWAY["Railway (hosting network)"]
    EDGE["Edge proxy<br/>TLS ENDS HERE<br/>Let's Encrypt cert"]
    APP["career-platform service<br/>uvicorn, 2 FastAPI workers"]
    PG[("Postgres service")]
  end

  GOOGLE["Google Tag Manager +<br/>Google Analytics"]

  LAPTOP -- "0 Wi-Fi join, DHCP: address, gateway = router, DNS = router" --- ROUTER
  ROUTER --- MODEM --- ISP --- NET

  LAPTOP -. "2 what is zetiantao.me?" .-> ROUTER
  ROUTER -. "2a forwarded" .-> RES
  RES -. "2b" .-> ROOT
  RES -. "2c" .-> TLD
  RES -. "2d" .-> CF
  RES -. "2e IP answer, back via router" .-> LAPTOP

  NET == "3-6 TCP, then TLS, then HTTPS<br/>public internet, source = my public address after NAT" ==> EDGE
  EDGE -- "7 plain HTTP<br/>private network" --> APP
  APP -- "8 SQL query<br/>private network" --> PG

  LAPTOP -. "10 after consent<br/>analytics events" .-> GOOGLE
```

## 2. Order of events for one page load (client → server on each arrow)

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser (laptop)
  participant H as Home router
  participant R as ISP recursive resolver
  participant N as Root / .me / Cloudflare DNS
  participant E as Railway edge proxy
  participant A as App (uvicorn + FastAPI)
  participant D as Postgres
  participant G as Google Analytics

  Note over B,H: Already joined Wi-Fi. DHCP gave a private address, gateway = router, DNS = router
  Note over B: Assume: new connection, nothing cached
  B->>B: Parse URL: scheme, name, path
  B->>H: DNS query for zetiantao.me
  H->>R: Forward query (NAT to public address)
  R->>N: Ask root, then .me, then Cloudflare
  N-->>R: Cloudflare answers with IP (flattened CNAME)
  R-->>H: IP of Railway edge
  H-->>B: IP of Railway edge
  B->>E: TCP handshake (through router: NAT + firewall, then ISP, then internet)
  B->>E: TLS handshake (name, certificate check)
  Note over E: TLS ends at the edge
  B->>E: HTTP request (if typed http, edge replies 301 to https first)
  E->>A: Forward as plain HTTP (private)
  A->>D: Query profile + projects (private)
  D-->>A: Rows (or error leads to cached profile + 503)
  A-->>E: Rendered HTML page
  E-->>B: Response over TLS (router's firewall lets it in as a reply, NAT maps it back to the laptop)
  B->>E: Separate requests: CSS, JS, fonts
  B->>G: After consent: page_view, click events (direct to Google)
```

## 3. Azure: where everything sits (2026-09-29 to 2026-10-10)

The site ran here before the Railway cutover. The VM has been deallocated since 2026-10-13. The home network and DNS chain are the same as on Railway. What differs: Cloudflare's answer is a plain A record pointing at the VM's public IP, and everything after the internet is one machine I run myself.

```mermaid
flowchart LR
  subgraph HOME["My home network (private addresses, e.g. 192.168.x.x)"]
    LAPTOP["Laptop<br/>browser + OS<br/>Wi-Fi card<br/>private address from DHCP"]
    ROUTER["Home router<br/>Wi-Fi access point + switch<br/>gateway + DHCP + DNS forwarder<br/>NAT + firewall"]
    MODEM["Modem / ONT<br/>(may be built into the router)"]
  end

  ISP["ISP network<br/>gives the router its one public address"]
  NET["Internet routers"]

  subgraph DNS["DNS (separate exchange)"]
    RES["ISP recursive resolver"]
    ROOT["Root servers"]
    TLD[".me TLD servers"]
    CF["Cloudflare<br/>authoritative DNS<br/>A record to the VM, DNS only"]
  end

  subgraph AZURE["Azure, North Central US (hosting network)"]
    PIP["Azure public IP<br/>mapped 1:1 to the VM's private address"]
    NSG["Network security group<br/>allows web from anyone<br/>SSH only from my IPs<br/>drops everything else"]
    subgraph VM["Ubuntu VM (private address in Azure's virtual network)"]
      NGINX["nginx<br/>TLS ENDS HERE<br/>certbot / Let's Encrypt cert<br/>redirects http to https"]
      APP["uvicorn, 2 FastAPI workers<br/>run by systemd, not root<br/>listens on loopback only"]
      DB[("SQLite file<br/>on the same disk")]
      TIMER["certbot.timer<br/>renews the cert"]
    end
  end

  GOOGLE["Google Tag Manager +<br/>Google Analytics"]

  LAPTOP -- "0 Wi-Fi join, DHCP: address, gateway = router, DNS = router" --- ROUTER
  ROUTER --- MODEM --- ISP --- NET

  LAPTOP -. "2 what is zetiantao.me?" .-> ROUTER
  ROUTER -. "2a forwarded" .-> RES
  RES -. "2b" .-> ROOT
  RES -. "2c" .-> TLD
  RES -. "2d" .-> CF
  RES -. "2e VM's public IP, back via router" .-> LAPTOP

  NET == "3-6 TCP, then TLS, then HTTPS<br/>public internet, source = my public address after NAT" ==> PIP
  PIP --> NSG
  NSG -- "only allowed traffic" --> NGINX
  NGINX -- "7 plain HTTP<br/>loopback, never leaves the VM" --> APP
  APP -- "8 file read<br/>no network at all" --> DB
  TIMER -. "renewal check through nginx" .-> NGINX

  LAPTOP -. "10 after consent<br/>analytics events" .-> GOOGLE
```

## 4. Azure: order of events for one page load (client → server on each arrow)

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser (laptop)
  participant H as Home router
  participant R as ISP recursive resolver
  participant N as Root / .me / Cloudflare DNS
  participant F as Azure public IP + NSG
  participant X as nginx (on the VM)
  participant A as App (uvicorn + FastAPI, on the VM)
  participant D as SQLite file (on the VM)
  participant G as Google Analytics

  Note over B,H: Already joined Wi-Fi. DHCP gave a private address, gateway = router, DNS = router
  Note over B: Assume: new connection, nothing cached
  B->>B: Parse URL: scheme, name, path
  B->>H: DNS query for zetiantao.me
  H->>R: Forward query (NAT to public address)
  R->>N: Ask root, then .me, then Cloudflare
  N-->>R: Cloudflare answers with the VM's public IP (A record)
  R-->>H: VM's public IP
  H-->>B: VM's public IP
  B->>F: TCP handshake (through router: NAT + firewall, then ISP, then internet)
  Note over F: NSG checks the rule list. Web is allowed, so Azure maps the public IP to the VM's private address
  F->>X: Connection reaches nginx
  B->>X: TLS handshake (name, certificate check)
  Note over X: TLS ends at nginx, inside the VM
  B->>X: HTTP request (if typed http, nginx replies 301 to https first)
  X->>A: Forward as plain HTTP over loopback, with the original host and https flag
  A->>D: Read profile + projects from the file
  D-->>A: Rows (or error leads to cached profile + 503)
  A-->>X: Rendered HTML page
  X-->>B: Response over TLS (back out through Azure, router's firewall lets it in as a reply, NAT maps it back to the laptop)
  B->>X: Separate requests: CSS, JS, fonts (nginx passes them to the app too)
  B->>G: After consent: page_view, click events (direct to Google)
```

Separate from the web path: I manage the VM over SSH with a key from my laptop. The NSG only lets SSH in from my own IP addresses.

## Things to say aloud

- The dotted DNS arrows never touch the web path.
- The thick arrow is the only part on the public internet.
- At home, one box plays many roles: access point, switch, router (gateway), DHCP server, DNS forwarder, NAT and firewall. The gateway and the DNS server have the same address but are different jobs.
- Everything inside the house uses private addresses. Railway only ever sees my one public address, because NAT rewrote it.
- On Railway everything after the edge is private; on Azure everything after nginx stays inside the VM.
- Who runs each layer: on Azure I ran the firewall rules, nginx, the certificate, systemd and the database file. On Railway the edge, the certificate and the Postgres server are the platform's, but the code, the data and DNS are still mine.
