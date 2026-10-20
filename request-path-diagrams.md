# Request path diagrams: entering zetiantao.me in a browser

Midterm study diagrams. Step numbers 0–10 match the step table:
0 network join, 1 parse URL, 2 DNS, 3 leaving the house, 4 TCP, 5 TLS, 6 redirect, 7 edge to app, 8 app to database, 9 response, 10 rest of the page.

## 1. Where everything sits (hardware, services, and the Railway host)

```mermaid
flowchart LR
  subgraph HOME["Home network (private addresses)"]
    LAPTOP["Laptop<br/>browser + OS<br/>Wi-Fi card"]
    ROUTER["Home router<br/>access point + switch<br/>gateway + DHCP + NAT + firewall"]
    MODEM["Modem / ONT"]
  end

  ISP["ISP network<br/>(public address on router)"]
  NET["Internet routers"]

  subgraph DNS["DNS (separate exchange)"]
    RES["Recursive resolver<br/>(ISP / router / 1.1.1.1 - unknown)"]
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

  LAPTOP -- "0 DHCP: address, gateway, DNS server" --- ROUTER
  ROUTER --- MODEM --- ISP --- NET

  LAPTOP -. "2 what is zetiantao.me?" .-> RES
  RES -. "2a" .-> ROOT
  RES -. "2b" .-> TLD
  RES -. "2c" .-> CF
  RES -. "2d IP answer" .-> LAPTOP

  NET == "3-6 TCP, then TLS, then HTTPS<br/>public internet" ==> EDGE
  EDGE -- "7 plain HTTP<br/>private network" --> APP
  APP -- "8 SQL query<br/>private network" --> PG

  LAPTOP -. "10 after consent<br/>analytics events" .-> GOOGLE
```

## 2. Order of events for one page load (client → server on each arrow)

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser (laptop)
  participant R as Recursive resolver
  participant N as Root / .me / Cloudflare DNS
  participant E as Railway edge proxy
  participant A as App (uvicorn + FastAPI)
  participant D as Postgres
  participant G as Google Analytics

  Note over B: Assume: new connection, nothing cached
  B->>B: Parse URL: scheme, name, path
  B->>R: DNS query for zetiantao.me
  R->>N: Ask root, then .me, then Cloudflare
  N-->>R: Cloudflare answers with IP (flattened CNAME)
  R-->>B: IP of Railway edge
  B->>E: TCP handshake
  B->>E: TLS handshake (name, certificate check)
  Note over E: TLS ends at the edge
  B->>E: HTTP request (if typed http, edge replies 301 to https first)
  E->>A: Forward as plain HTTP (private)
  A->>D: Query profile + projects (private)
  D-->>A: Rows (or error leads to cached profile + 503)
  A-->>E: Rendered HTML page
  E-->>B: Response over TLS
  B->>E: Separate requests: CSS, JS, fonts
  B->>G: After consent: page_view, click events (direct to Google)
```

## 3. What changes on the Azure host

Replace the Railway box in diagram 1 with this. Everything to the left stays the same.

```mermaid
flowchart LR
  NET["Internet routers"] == "TCP, TLS, HTTPS" ==> NSG
  subgraph AZURE["Azure VM (Ubuntu)"]
    NSG["Azure firewall (NSG)<br/>web open, SSH only from my IPs"]
    NGINX["nginx<br/>TLS ENDS HERE<br/>certbot certificate"]
    UV["uvicorn, 2 workers<br/>managed by systemd<br/>loopback only"]
    DB[("SQLite file<br/>same machine")]
    NSG --> NGINX -- "plain HTTP, loopback" --> UV -- "file read" --> DB
  end
```

## Things to say aloud

- The dotted DNS arrows never touch the web path.
- The thick arrow is the only part on the public internet.
- On Railway everything after the edge is private; on Azure everything after nginx stays inside the VM.
