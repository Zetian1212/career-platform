# Operate the VM Plan

**Goal:** Run the career platform like a real website. Visitors open `http://172.183.16.158` with no port number. The site starts when the VM boots and comes back on its own after a crash. Port 8000 stays private, and the app never runs as root.

**Target (found with Azure CLI, read-only, 2026-10-05):**

| | |
|---|---|
| VM | `vm-career-platform`, resource group `rg-career-platform`, subscription "Azure for Students" |
| Region / size | northcentralus, `Standard_B2ats_v2` (2 vCPU, ~890 MB RAM) |
| OS | Ubuntu 24.04 LTS |
| Public IP | `172.183.16.158` (private `10.0.0.4`, no DNS name) |
| SSH | `ssh -i ~/.ssh/isba4775_azure azureuser@172.183.16.158` (password login disabled) |
| Firewall (NSG `vm-career-platformNSG`) | One inbound rule: `Allow-SSH-Laptop`, port 22 from your laptop IP only |
| App | `~/career-platform` at `92832fa`, Python 3.12.3 in `.venv`, uvicorn 0.54.0, config in `.env`, data in `career_platform.db` |
| State when planned | **Down.** The VM restarted at 18:55 UTC and nothing started uvicorn again. nginx is not installed. (Up again since step 1.3; see Restart check.) |

**Status:** Sections 1–2 done (2026-10-05). You added `Allow-HTTP-80` (Section 3), and the Restart check below passed, including a real reboot. Section 4's outside checks have not been run as a set yet.

## How it fits together

```
Browser ──port 80──▶ Azure firewall (Allow-HTTP-80) ──▶ nginx (port 80)
                                                          │
                                       127.0.0.1:8000 ◀───┘  (only reachable from inside the VM)
                                              │
                         systemd service "career-platform", runs as azureuser
                             uvicorn manager ─┬─ worker 1
                                              └─ worker 2
```

- **nginx** is a small, sturdy web server. It listens on port 80 (the port browsers use when there's no number in the URL) and hands each request to the app. It's the only thing the Internet talks to.
- **systemd** is Ubuntu's service manager. It starts programs at boot and restarts them if they die. We give it a "unit file" that says how to run the app.
- **Two uvicorn workers** are two copies of the app behind one manager process. If one worker crashes, the other keeps serving while the manager replaces it. If the whole thing dies, systemd starts it again.
- **Port 8000 stays private** because uvicorn only listens on `127.0.0.1`, which is reachable from inside the VM only, and because no firewall rule opens 8000.

Each step lists **Where** (laptop, VM or portal), **Run**, **Why**, **Check** and **Undo**. "VM" means inside an SSH session opened with the SSH command above. None of the steps change files in the repo. The new files live in `/etc`.

---

## 1. Run the app as a service

- [ ] **1.1 Make sure nothing is on port 8000**
  - **Where:** VM
  - **Run:** `ss -ltnp | grep 8000 || echo free`, then `rm -f ~/uvicorn.pid`
  - **Why:** The old `nohup` uvicorn died when the VM restarted, so the port should be free. If something is still there, the service can't start. The PID file is left over from that old process.
  - **Check:** Prints `free`. If it shows a process, stop it with `kill <PID>` (avoid `pkill -f` over SSH; see the 2026-09-24 plan's Lessons).
  - **Undo:** Nothing to undo.

- [ ] **1.2 Create the systemd unit**
  - **Where:** VM
  - **Run:**
    ```bash
    sudo tee /etc/systemd/system/career-platform.service > /dev/null <<'EOF'
    [Unit]
    Description=Career platform (uvicorn)
    After=network.target

    [Service]
    User=azureuser
    Group=azureuser
    WorkingDirectory=/home/azureuser/career-platform
    ExecStart=/home/azureuser/career-platform/.venv/bin/uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 2
    Restart=always
    RestartSec=3

    [Install]
    WantedBy=multi-user.target
    EOF
    ```
  - **Why, line by line:**
    - `User=azureuser` keeps the app from running as root.
    - `WorkingDirectory` is required because `.env` and `DATABASE_URL=sqlite:///./career_platform.db` are relative paths.
    - `ExecStart` calls the `.venv` uvicorn directly. That avoids depending on `uv` being on the PATH, which it isn't for non-interactive shells.
    - `--host 127.0.0.1` keeps port 8000 private, and `--workers 2` matches the 2 vCPUs.
    - `Restart=always` brings the service back 3 seconds after any exit.
    - `WantedBy=multi-user.target` is what lets `enable` start it at boot.
  - **Check:** `systemd-analyze verify /etc/systemd/system/career-platform.service` prints no errors.
  - **Undo:** `sudo rm /etc/systemd/system/career-platform.service && sudo systemctl daemon-reload`

- [ ] **1.3 Start it now and at every boot**
  - **Where:** VM
  - **Run:** `sudo systemctl daemon-reload && sudo systemctl enable --now career-platform`
  - **Why:** `daemon-reload` makes systemd read the new file. `enable` turns on start-at-boot, and `--now` also starts the service right away.
  - **Check:**
    - `systemctl is-enabled career-platform` prints `enabled`, and `systemctl is-active career-platform` prints `active`.
    - `curl -s http://127.0.0.1:8000/healthz` returns `{"status":"ok"}`.
    - `ps -o user:12,pid,ppid,cmd --ppid <MAIN_PID> --pid <MAIN_PID>` (get `<MAIN_PID>` from `systemctl show -p MainPID career-platform`) lists 3 processes, all owned by `azureuser`: the uvicorn manager and two workers. The workers show up as `python -c from multiprocessing.spawn …`, not as `uvicorn`, so `grep uvicorn` only finds the manager.
    - `ss -ltnp | grep 8000` shows `127.0.0.1:8000` only.
  - **Undo:** `sudo systemctl disable --now career-platform`
  - **Logs:** The app now logs to the journal instead of `~/uvicorn.log`. Read them with `journalctl -u career-platform -n 50`.

### Section 1 results (2026-10-05, ~19:27 UTC)

Every step ran over `ssh … 'cmd'` from the laptop. All checks **passed**.

| Step | What ran | What the check showed |
|---|---|---|
| 1.1 | `ss -ltnp \| grep 8000 \|\| echo free`, `rm -f ~/uvicorn.pid` | Printed `free`. The stale `~/uvicorn.pid` (dated Sep 30 01:37) was deleted. |
| 1.2 | `sudo tee /etc/systemd/system/career-platform.service` with the unit above, exactly as written | File is `root:root`, mode `644`, 354 bytes. `systemd-analyze verify` printed nothing and exited `0`. |
| 1.3 | `sudo systemctl daemon-reload && sudo systemctl enable --now career-platform` | Created the `multi-user.target.wants` symlink. `is-enabled` → `enabled`, `is-active` → `active`. `/healthz` → `{"status":"ok"}`. `/`, `/resume`, `/portfolio` → 200. Home `<h1>` is `Zetian Tao` (from the DB, no fallback). |
| 1.3 processes | `ps -o user:12,pid,ppid,cmd --pid 2023,2026,2027` | Manager PID 2023 (parent 1 = systemd) plus workers 2026 and 2027 (parent 2023), all `azureuser`. No root-owned uvicorn/app process. |
| 1.3 port | `ss -ltnp \| grep 8000` | Only `127.0.0.1:8000`, held by 2023, 2026 and 2027. |
| 1.3 logs | `journalctl -u career-platform -n 15` | `Started parent process [2023]`, both workers `Application startup complete`, and the test requests logged as 200. No errors. |

**Deviation:** the plan's original `ps … -C uvicorn` check would have missed the two workers, because they run as `python -c from multiprocessing.spawn …`. The check above has been corrected to list them by PID.

## 2. Put nginx in front on port 80

- [ ] **2.1 Install nginx**
  - **Where:** VM
  - **Run:** `sudo apt-get update && sudo apt-get install -y nginx`
  - **Why:** nginx answers on port 80 and passes requests to the app. Ubuntu's package enables it at boot and starts it right after installing. Its worker processes run as `www-data`, not root. Only a tiny master process needs root, so it can open port 80.
  - **Check:** `systemctl is-enabled nginx` prints `enabled`, and `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/` prints `200` (the nginx welcome page for now).
  - **Undo:** `sudo apt-get purge -y nginx nginx-common && sudo apt-get autoremove -y`

- [ ] **2.2 Point nginx at the app**
  - **Where:** VM
  - **Run:**
    ```bash
    sudo tee /etc/nginx/sites-available/career-platform > /dev/null <<'EOF'
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    EOF
    sudo ln -s /etc/nginx/sites-available/career-platform /etc/nginx/sites-enabled/career-platform
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
    ```
  - **Why:** `proxy_pass` forwards every request to the app on `127.0.0.1:8000`. The `proxy_set_header` lines pass along the original host and visitor address. `default_server` plus removing the stock `default` site make this site the one that answers requests by IP address. Removing it only deletes a link, and the original stays in `sites-available`. `nginx -t` checks the syntax before `reload` applies it, so a typo can't take nginx down.
  - **Check:** Wait a couple of seconds after the reload, then `curl -s http://127.0.0.1/ | grep -o "<h1>[^<]*"` shows `<h1>Zetian Tao`, from the app rather than the nginx welcome page. (`reload` returns before the old nginx workers have handed over, so a check run immediately can still see the welcome page.)
  - **Undo:** `sudo rm /etc/nginx/sites-enabled/career-platform && sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && sudo systemctl reload nginx`

- [ ] **2.3 Make nginx restart itself too**
  - **Where:** VM
  - **Run:**
    ```bash
    sudo mkdir -p /etc/systemd/system/nginx.service.d
    printf '[Service]\nRestart=on-failure\nRestartSec=3\n' | sudo tee /etc/systemd/system/nginx.service.d/restart.conf > /dev/null
    sudo systemctl daemon-reload
    ```
  - **Why:** Ubuntu's nginx unit doesn't restart on a crash. This small "drop-in" file adds that without editing the packaged unit. Now neither layer can stay down after a crash.
  - **Check:** `systemctl show nginx -p Restart` prints `Restart=on-failure`.
  - **Undo:** `sudo rm -r /etc/systemd/system/nginx.service.d && sudo systemctl daemon-reload`

### Section 2 results (2026-10-05, ~19:33 UTC)

Every step ran over `ssh … 'cmd'` from the laptop. All checks **passed** (2.2 on the second look; see below).

| Step | What ran | What the check showed |
|---|---|---|
| 2.1 | `sudo apt-get update && sudo apt-get install -y nginx` | Installed nginx 1.24.0 (Ubuntu). needrestart reported nothing to restart. `is-enabled` → `enabled`, `is-active` → `active`. `http://127.0.0.1/` → 200 with `<title>Welcome to nginx!`. Processes: master PID 2787 as `root`, two workers as `www-data`. |
| 2.2 | Wrote `/etc/nginx/sites-available/career-platform` exactly as above, linked it into `sites-enabled`, removed the `default` link, then `nginx -t && systemctl reload nginx` | `nginx -t`: syntax ok, test successful. `sites-enabled` holds only `career-platform`; `sites-available/default` is still there for Undo. |
| 2.2 first check | `curl` right after the reload | **Still the welcome page**: `/` 200 with `<h1>Welcome to nginx!`, and `/resume`, `/portfolio`, `/healthz` 404. |
| 2.2 recheck | Same `curl`s a few seconds later, plus `nginx -T` | `<h1>Zetian Tao`, no "cached profile" banner. `/`, `/resume`, `/portfolio`, `/healthz`, `/static/css/site.css` all 200. `nginx -T` shows only one server block (`career-platform`, `listen 80 default_server`, `proxy_pass http://127.0.0.1:8000`). The journal shows the reload finished at 19:33:13. |
| 2.2 ports | `ss -ltnp` | nginx on `0.0.0.0:80` and `[::]:80`; the app still on `127.0.0.1:8000` only. |
| 2.3 | Wrote `/etc/systemd/system/nginx.service.d/restart.conf`, `daemon-reload` | `systemctl show nginx` → `Restart=on-failure`, `RestartUSec=3s`, `DropInPaths=/etc/systemd/system/nginx.service.d/restart.conf`. nginx still `active`, `/` still 200. |

**Why the first 2.2 check failed:** a race, not a config problem. `systemctl reload` returns as soon as nginx is signalled, while the old workers (still using the default site) keep answering for a moment. Nothing was changed between the two checks. The 2.2 Check now says to wait a couple of seconds.

**Not tested yet:** reaching port 80 from the Internet. Azure still blocks it until you add `Allow-HTTP-80` (Section 3).

## 3. Open port 80 in Azure (you do this)

- [ ] **3.1 Add `Allow-HTTP-80`**
  - **Where:** portal: VM → Networking → Add inbound port rule
  - **Run:** Source = Any; Destination port = `80`; Protocol = TCP; Action = Allow; Priority = `320`; Name = `Allow-HTTP-80`.
  - **Why:** Azure's firewall (the NSG) drops everything that isn't explicitly allowed. This opens port 80 only. Don't add a rule for 8000.
  - **Check (laptop):** `az network nsg rule list -g rg-career-platform --nsg-name vm-career-platformNSG -o table` shows `Allow-SSH-Laptop` (22) and `Allow-HTTP-80` (80), and nothing for 8000.
  - **Undo:** Delete the rule in the portal.

## 4. Verify from outside

- [ ] **4.1 The site works at the bare IP**
  - **Where:** laptop
  - **Run:** `for p in / /resume /portfolio /healthz; do curl -s -o /dev/null -w "$p %{http_code}\n" http://172.183.16.158$p; done`, then open `http://172.183.16.158` in a browser.
  - **Check:** Every line ends in `200`, and the browser shows your name with no "cached profile" banner.

- [ ] **4.2 Port 8000 is closed to the Internet**
  - **Where:** laptop
  - **Run:** `curl -s --max-time 5 http://172.183.16.158:8000/ ; echo "exit $?"`
  - **Check:** It prints `exit 28` (timeout), because Azure drops the traffic. Any page content means 8000 is open, and that would be a failure.

- [ ] **4.3 Settings that make it survive a boot**
  - **Where:** VM
  - **Run:** `systemctl is-enabled career-platform nginx`
  - **Check:** Both print `enabled`. This proves the services are set to start at boot without rebooting the VM. Crash and reboot tests are left for you to run.

---

## Restart check

You ran these tests on 2026-10-05. Everything ran on the VM except the NSG check. All times are UTC.

**Why it matters:** these show the three layers of recovery working: systemd at boot, uvicorn replacing a dead worker, and systemd replacing a dead manager. They also show what a visitor sees in the gaps between.

### Boot, service start, and the page through nginx

| What | Command | Result |
|---|---|---|
| Last boot | `uptime -s`, `journalctl --list-boots` | Read at 21:11:11: boot at **18:55:32** (Azure start after the 18:53 deallocate). Then **the VM rebooted again at ~21:11:15**: the previous boot's last journal entry is 21:11:15, and a new boot ID `be85e624…` follows. |
| Service start before that reboot | `systemctl show career-platform -p ActiveEnterTimestamp` | **19:27:40**, when step 1.3 started it by hand. NRestarts 0, main PID 2023. |
| Service start after that reboot | same | **21:11:31**, started by systemd at boot with no manual command. Main PID 667, workers ready at 21:11:36. This is the boot-start proof. |
| Page through nginx | `curl -i http://127.0.0.1/` on the VM | `HTTP/1.1 200 OK`, `Server: nginx/1.24.0 (Ubuntu)`, `<h1>Zetian Tao`, which matches `select name from profile`. No "cached profile" banner. |
| Port 80 in Azure | `az network nsg rule list` (laptop, read-only) | `Allow-HTTP-80`, priority 320, port 80 from `*`, next to `Allow-SSH-Laptop`. No 8000 rule. The journal shows requests from your laptop IP getting 200 through nginx (21:09:43 and 21:12:19). |
| Gap during that boot | nginx `error.log` | Laptop requests at **21:11:35** got **502** (`connect() failed (111: Connection refused)`, upstream `127.0.0.1:8000`). nginx was up before the app's workers finished starting at 21:11:36. It cleared on its own about a second later. |

### Crash and stop tests

| Test | What ran | What happened | Visitor sees |
|---|---|---|---|
| Kill one worker | 21:12:01 `kill -9 857` (worker; manager is 667) | 857 shows `<defunct>` right away. The journal shows `Child process [857] died` → `Started server process [1211]` → `Application startup complete` at 21:12:02. Main PID still 667, service `active (running)` since 21:11:31, not restarted. | 200 throughout. The other worker (858) kept serving. |
| Kill the main process | 21:12:14 `kill -9 667` (no systemctl) | Status #1 (21:12:15): `activating (auto-restart) (Result: signal)`, `Main PID: 667 (code=killed, signal=KILL)`. Status #2 (21:12:20): `active (running) since 21:12:17`, new main PID 1287 with workers 1289/1290. `NRestarts=1`. No old workers were left behind. | **502 for ~3 s** (`RestartSec=3` plus startup), then 200. |
| Stop with systemctl | 21:12:26 `sudo systemctl stop career-platform` | `inactive`, nothing on port 8000. `http://localhost` → `HTTP/1.1 502 Bad Gateway` from `nginx/1.24.0 (Ubuntu)`. error.log: `connect() failed (111: Connection refused) … client: ::1 … upstream: "http://127.0.0.1:8000/", host: "localhost"`. systemd did **not** restart it, which is expected: `Restart=always` doesn't apply to a deliberate stop. | 502 until started |
| Start again | 21:12:31 `sudo systemctl start career-platform` | `active (running)`, main PID 1413, workers 1416/1417 ready at 21:12:32. `http://localhost` → 200, `<h1>Zetian Tao`. | 200 |

**What this shows:** a worker crash costs nothing. A manager crash or a reboot costs a few seconds of nginx 502s. A manual `stop` keeps the site down until someone runs `start`. nginx's own crash restart (step 2.3) was not tested.

## Record

A snapshot of how the VM is exposed, taken 2026-10-05 after the Restart check. Your laptop's address is written as `<LAPTOP_IP>`, and no subscription or tenant IDs are recorded.

### Listening TCP ports

Taken from `sudo ss -ltnp` on the VM. An address of `0.0.0.0` or `[::]` means "every network interface", so the port can be reached from outside if the Azure firewall allows it. `127.x.x.x` means "this VM only".

| Address:Port | Program | Reachable from | Why it's there |
|---|---|---|---|
| `0.0.0.0:80`, `[::]:80` | `nginx` (master 765 as root, workers 767/768 as `www-data`) | Internet, via `Allow-HTTP-80` | The public website. It passes requests to the app on port 8000. |
| `0.0.0.0:22`, `[::]:22` | `sshd` (1007; the socket is held by `systemd`, PID 1) | Your laptop only, via `Allow-SSH-Laptop` | Admin login. |
| `127.0.0.1:8000` | `uvicorn` manager 1413 plus `python` workers 1416/1417, all `azureuser` | Inside the VM only | The app. Only nginx talks to it. |
| `127.0.0.53%lo:53`, `127.0.0.54:53` | `systemd-resolve` (528) | Inside the VM only | Ubuntu's local DNS resolver. |

The PIDs are from this snapshot and change on every restart. (`sudo ss -lunp` also shows UDP listeners, all local or DHCP: `chronyd` time sync on `127.0.0.1:323`/`[::1]:323`, `systemd-resolve` on `:53`, and the DHCP client on `10.0.0.4:68`.)

### IP addresses

| | Address | Where it comes from |
|---|---|---|
| Private | `10.0.0.4` (`eth0`, `/24`) | The Azure virtual network. Only reachable inside it. |
| Public | `172.183.16.158` | Azure public IP resource. This is the site's address. It isn't set to delete with the VM. |

Checked with `az vm list-ip-addresses` (laptop) and `ip -4 -br addr` (VM). They agree.

### Inbound rules (NSG `vm-career-platformNSG`)

Azure checks the rules from the lowest priority number upward and stops at the first match.

| Priority | Name | Allows | From | Why it exists |
|---|---|---|---|---|
| 300 | `Allow-SSH-Laptop` | TCP 22 | `<LAPTOP_IP>/32` | Lets you SSH in to run and fix the VM, from one address only, so no one else can even try to log in. Update it when your network changes. |
| 320 | `Allow-HTTP-80` | TCP 80 | Any | Lets everyone reach the website through nginx. Added by you for Section 3. |
| 65000 | `AllowVnetInBound` (Azure default) | All | Virtual network | Traffic between resources in the same Azure network. Nothing else lives there now. |
| 65001 | `AllowAzureLoadBalancerInBound` (Azure default) | All | Azure load balancer | Azure's own health probes. |
| 65500 | `DenyAllInBound` (Azure default) | — (denies) | Any | Drops everything not allowed above. This is why port 8000 isn't reachable from outside. |

There's no rule for port 8000, and none is needed.

## Full rollback

Run these in reverse order: delete `Allow-HTTP-80` (undo 3.1), undo 2.3, undo 2.2, undo 2.1, then undo 1.3 and 1.2. The repo, `.venv`, `.env` and the database are never touched, so going back to the old `nohup` start (2026-09-24 plan, step 7.1) still works.

## Day-to-day commands (VM)

| Task | Command |
|---|---|
| Status | `systemctl status career-platform nginx` |
| App logs | `journalctl -u career-platform -f` |
| Restart after `git pull` | `sudo systemctl restart career-platform` |
| Stop / start | `sudo systemctl stop career-platform` / `sudo systemctl start career-platform` |

## Progress log

- **2026-10-07, read-only check (laptop and VM).** The site is served at **https://zetiantao.me**: `/`, `/resume` and `/healthz` return 200, and `http://zetiantao.me/` redirects 301 to https. nginx's `career-platform` site now has `server_name zetiantao.me www.zetiantao.me` and Certbot-managed `listen 443 ssl` blocks (`sites-enabled/` last changed 2026-10-06 22:02). Requests to the bare IP `http://172.183.16.158/` now get nginx's own **404**. That is Certbot's default for any host name it doesn't manage, not an outage. Services: `career-platform` and `nginx` both `active`; the app answers `127.0.0.1:8000/healthz` with 200. The VM booted at 2026-10-06 20:59:32 UTC.
- **Deploy note.** On the VM, `~/career-platform` is at `8559101` and `git status` shows `career_platform.db` modified (live data) plus an untracked `career_platform.db.from-git`. Before any `git pull`, back up the database and confirm the incoming commits don't touch `career_platform.db`.
- **2026-10-07 ~16:46 UTC, deploy of PR #1 (redesign).** Backed up the live DB to `~/career_platform.db.bak-20261007T164627Z`, confirmed the incoming commits did not touch `career_platform.db`, then `git pull --ff-only origin main` (now `76d0f06`) and `sudo systemctl restart career-platform`. Service `active`, `/healthz` 200. From the laptop, `https://zetiantao.me` `/`, `/resume`, `/portfolio`, `/portfolio/career-platform`, `/contact`, the font file and `/healthz` return 200, and unknown paths return the new HTML 404. The page shows "Live database" with no cached banner.
- **2026-10-07 ~16:47 UTC, content edit.** Backed up the DB again (`~/career_platform.db.bak-20261007T164652Z-pre-summary`), then removed the trailing "Source: github.com/Zetian1212/career-platform" sentence from the `career-platform` project summary with a single `UPDATE … WHERE slug = 'career-platform' AND summary = <old text>` (1 row changed). The repo stays linked through the project's `repo_url`.
- **2026-10-07 ~17:00 UTC, rollback of the redesign.** At your request, checked out `8559101` on the VM (detached HEAD; the merge did not touch `career_platform.db`) and ran `sudo systemctl restart career-platform`. `https://zetiantao.me` serves the previous design again; `/`, `/resume`, `/portfolio` and `/contact` return 200. **`main` on GitHub still contains the redesign (`76d0f06`)**, so don't `git pull` on the VM until a replacement design is merged. When deploying next, return to the branch with `git checkout main` first. The project-summary edit above stays in place.
