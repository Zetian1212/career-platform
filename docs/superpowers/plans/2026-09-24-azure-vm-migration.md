# Azure VM Migration Plan

**Goal:** Run the career platform on the Azure VM so it serves the same data as the laptop copy.

**Target:** VM `vm-career-platform` in resource group `rg-career-platform` (North Central US, `Standard_B2ats_v2`, Ubuntu 24.04). Public IP `172.183.16.158`, user `azureuser`, key `~/.ssh/isba4775_azure`.

**Source:** Public GitHub repo `https://github.com/Zetian1212/career-platform`, branch `main`.

**Status:** Complete (2026-09-29). All steps pass. The site runs on the VM (`127.0.0.1:8000`, reached through an SSH tunnel) and serves content from the database. The starter content is minimal; replace it through `/admin`.

**Tools:** Azure CLI 2.90.0 (Homebrew) on the laptop, logged in to the "Azure for Students" subscription. Every `az` step runs from the laptop, so the VM doesn't need Azure CLI.

## Progress log

- **2026-09-24:** VM created (see Target). Plan written.
- **2026-09-29:** Checked: VM running. Found SSH rule `Allow-SSH-Laptop` (port 22 from `157.242.208.200/32`), which you added yourself; that completes 1.2. Confirmed Azure CLI is installed on the laptop.
- **2026-09-29:** Laptop IP still `157.242.208.200`. SSH login worked (step 1.3); VM up 4 days 23 h, load 0.00, 1 other user session open.
- **2026-09-29:** Step 2.1: `apt-get update` succeeded. git was already installed (2.43.0, part of the Ubuntu image), so only sqlite3 3.45.1 was added. needrestart reported no services to restart.
- **2026-09-29:** Step 3.1: cloned to `~/career-platform` on the VM at `a813b76`, the same commit as the laptop and `origin/main`. The cloned `career_platform.db` has the same SHA-256 (`2eb782a1…43e31c1`) as the laptop copy, which is still empty (blocker 2). This plan file itself is uncommitted on the laptop, so it isn't on the VM.
- **2026-09-29:** Step 4.1: installed uv 0.12.19 on the laptop with Homebrew. The first test run **failed**: `RuntimeError: Form data requires "python-multipart"`. The admin form routes need that package, but `requirements.txt` never listed it, so the bug predates this migration. Added it to `pyproject.toml` and `requirements.txt`, and pinned Python 3.12 to match the VM. Tests then passed (10 passed on 3.12.14). Committed `pyproject.toml`, `uv.lock`, `.python-version` and `requirements.txt` as `d394885` and pushed to `main`. The plan file was left out of the commit.
- **2026-09-29:** Steps 4.2–4.3: installed uv 0.12.21 on the VM, ran `git pull` to `d394885`, then `uv sync --locked` succeeded on system Python 3.12.3. Imports were ok, `uv run pytest -q` passed 10 tests, and the VM's working tree is clean. Undo for 4.1 is now `git revert d394885`.
- **2026-09-29:** You approved Section 4 three more times. It was already done, so nothing was rerun, and commit `d394885` stays.
- **2026-09-29:** Step 5.1: created `~/career-platform/.env` from `.env.example` with mode `600`. `SESSION_SECRET` is 64 random hex characters; `ADMIN_PASSWORD` is a random 23-character value. No `change-me` / `change-this` defaults are left. git ignores `.env`, and `app.config` loads it (checked without printing the values). Found along the way: `uv` isn't on the PATH in non-interactive SSH commands; `~/.bashrc` only adds it for interactive shells. Commands run as `ssh … 'cmd'` must use `~/.local/bin/uv`; step 7.1 has been updated.
- **2026-09-29:** Looked for the real database. The laptop repo copy, the VM clone, and a search of the laptop home folder for `career_platform*.db` all turned up only the same empty file (0 profile rows, 0 projects). The 2026-09-15 build plan says development ran in GitHub Codespaces, so the data is probably in a Codespace's `career_platform.db`. `gh` is not installed on the laptop. Download options: the Codespace web UI (right-click the file → Download), or `brew install gh` + `gh auth login` + `gh codespace cp`.
- **2026-09-29:** Step 6.1: backed up the VM's cloned DB to `career_platform.db.from-git`. Step 6.2 is on hold.
- **2026-09-29:** Dropped the Codespace download (installed `gh` 2.101.0 on the laptop but never logged in). You chose the laptop repo DB for step 6.2. Checked it again: still 0 rows in profile, project, experience and skill. Copied it with scp; the VM hash matches `2eb782a1…43e31c1`, identical to the clone, so no data changed. Expect step 8.2 ("shows my data") to fail until real content is loaded.
- **2026-09-29:** Step 7.1: checked that port 8000 was free, then started uvicorn with `nohup ~/.local/bin/uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 > ~/uvicorn.log 2>&1 < /dev/null &`. The log shows `Application startup complete` and `Uvicorn running on http://127.0.0.1:8000`. `ss` shows it listening on 127.0.0.1:8000 only. It was still running from a new SSH session after the first one closed. It won't survive a VM reboot. If `kill $(cat ~/uvicorn.pid)` leaves the child running, use `pkill -f "uvicorn app.main"`.
- **2026-09-29:** Section 8: 8.1 passed (healthz and all four public pages return 200). 8.2 failed as expected: `select name from profile` returns no row, and the page `<h1>` is "Demo Candidate", which comes from `app/static/fallback/profile.json`. Note that the banner says "database is unavailable" even though the DB is reachable and only empty; the app shows the fallback whenever no profile is published. 8.3 passed: laptop port 8000 was free, and the tunnel started in the background (ssh PID 74461) serves the same pages at `http://localhost:8000`.
- **2026-09-29:** Re-ran 8.2: still **FAIL**, and nothing has changed. The DB hash is still `2eb782a1…43e31c1`, with 0 profile rows (0 published) and 0 projects. The home page `<h1>` is "Demo Candidate" with the cached-profile banner, and `/portfolio` has 0 project links. uvicorn is still listening.
- **2026-09-29:** Checked `~/Downloads/career_platform.db` (downloaded 15:01) as a candidate real DB. It's **byte-identical** to the repo copy (SHA-256 `2eb782a1…43e31c1`). The integrity check is ok, but all 9 tables have 0 rows. It wasn't copied to the VM because it would change nothing. 8.2 is still blocked on real content.
- **2026-09-29:** You asked me to finish everything. I backed up the VM DB to `~/career_platform.db.before-content`, then submitted content through the app's own admin forms. `curl` ran on the VM against `127.0.0.1`, reading the password from `.env` so it never left the VM. Login, profile and project all returned 303 → `/admin`. The content uses only facts I could verify: profile name "Zetian Tao" (git author), headline "Student, Loyola Marymount University" (from the `lion.lmu.edu` account), a one-line summary of this project, and one published, featured project "Career Platform" (`/portfolio/career-platform`). **Placeholders:** replace or extend them with your real headline, summary, education, links and projects via `/admin`.
- **2026-09-29:** Re-ran 8.2: **PASS**. The home page `<h1>` is "Zetian Tao" (same through the laptop tunnel), there's no cached-profile banner, `/portfolio` lists the project, `/portfolio/career-platform` returns 200, and all public pages plus `/healthz` return 200 with no 5xx or tracebacks in `~/uvicorn.log`.
- **Data location note:** the real content now lives **only in the VM's** `~/career-platform/career_platform.db`. The git-tracked copy on the laptop and GitHub is still empty. On the VM, `git status` shows that DB as modified; don't `git checkout`/`reset` it there. Back it up with `scp azureuser@172.183.16.158:~/career-platform/career_platform.db ~/Downloads/career_platform.vm-backup.db`.
- **Undo for the content step:** stop uvicorn, run `cp ~/career_platform.db.before-content ~/career-platform/career_platform.db`, then start uvicorn again.
- **2026-09-29 (post-migration):** Replaced the placeholder content with your LinkedIn export (`~/Downloads/Profile.pdf`). Backed up the VM DB to `~/career_platform.db.before-linkedin`, then ran a one-off loader (`~/load_linkedin_profile.py` on the VM). It loaded the profile (headline, LA location, summary), 3 internships with dates and bullets, 2 schools, 5 certifications, 9 skills, and LinkedIn/GitHub/email links, and added the repo, tech and role to the Career Platform project. A dry run on a local copy first confirmed the loader gives the same result when run twice. The live home page now shows the new headline.
- **Pending deploy:** template and CSS changes (dates, bullet lists, location, certifications, project tech/repo link), a regenerated fallback `profile.json`, and an updated test are on the laptop, **uncommitted**; the tests pass (10 passed). To deploy: commit and push, then on the VM run `git pull` and restart uvicorn (7.1 Undo, then 7.1). Before pulling, the VM's modified `career_platform.db` must be protected: `git pull` doesn't touch it unless the commit changes that file, and this commit doesn't.

Each step lists **Where** (laptop, VM or portal), **Run**, **Why**, **Check** and **Undo**. "VM" means inside an SSH session opened with:

```bash
ssh -i ~/.ssh/isba4775_azure azureuser@172.183.16.158
```

## Blockers found while writing this plan

Resolve these before starting. Each one is also covered by a step below.

1. ~~**There is no lock file.**~~ Resolved 2026-09-29 in commit `d394885` (step 4.1). The repo has only `requirements.txt`: no `pyproject.toml` and no `uv.lock`, so `uv sync` has nothing to sync. Step 4.1 creates them on the laptop and pushes them. uv is not installed on the laptop yet.
2. ~~**The laptop database is empty.**~~ Worked around 2026-09-29: content was entered on the VM through `/admin` instead (step 8.2). `./career_platform.db` has the tables, but `profile` and `project` both have 0 rows. SHA-256: `2eb782a1…43e31c1`. If your real data lives in a different `.db` file, use that path in step 6.2. Otherwise "shows my data" can't pass.
3. **The database is committed to git.** `career_platform.db` is tracked, so `git clone` already puts a copy on the VM. Step 6 overwrites that copy, and afterwards `git status` on the VM will show it as modified. That's expected.
4. ~~**SSH is closed.**~~ Resolved 2026-09-29: rule `Allow-SSH-Laptop` now allows port 22 from your IP (step 1.2).
5. **Port 8000 stays closed.** uvicorn listens on `127.0.0.1` only, and step 8 reaches it from the laptop through an SSH tunnel. Opening the site to the public is outside this plan.

---

## 1. Server

Azure VM, already created, reached over SSH.

- [x] **1.1 Confirm the VM is running** — done 2026-09-29 (`VM running`)
  - **Where:** laptop
  - **Run:** `az vm get-instance-view -g rg-career-platform -n vm-career-platform --query "instanceView.statuses[1].displayStatus" -o tsv`
  - **Why:** None of the later steps can work while the VM is stopped or deallocated.
  - **Check:** The output is `VM running`. If it's stopped, run `az vm start -g rg-career-platform -n vm-career-platform`.
  - **Undo:** Nothing to undo; this step only reads.

- [x] **1.2 Allow SSH from this laptop's IP only** — done by you before 2026-09-29, as rule `Allow-SSH-Laptop` (use that name in Undo instead of `allow-ssh-laptop`). If your IP changes, update the rule's source address.
  - **Where:** laptop (`az`), or the portal: VM → Networking → Add inbound port rule
  - **Run:** Check your current IP first with `curl -4 -s https://api.ipify.org`. It was `157.242.208.200` on 2026-09-24. Then:
    ```bash
    az network nsg rule create -g rg-career-platform --nsg-name vm-career-platformNSG \
      -n allow-ssh-laptop --priority 1000 --direction Inbound --access Allow \
      --protocol Tcp --destination-port-ranges 22 --source-address-prefixes 157.242.208.200/32
    ```
    Portal equivalent: source = IP addresses, `157.242.208.200/32`; service = SSH; action = Allow; priority = 1000; name = `allow-ssh-laptop`.
  - **Why:** The VM was created with no public inbound ports. This opens SSH to one address instead of the whole internet.
  - **Check:** `az network nsg rule list -g rg-career-platform --nsg-name vm-career-platformNSG -o table` shows the rule.
  - **Undo:** `az network nsg rule delete -g rg-career-platform --nsg-name vm-career-platformNSG -n allow-ssh-laptop`

- [x] **1.3 Log in over SSH** — done 2026-09-29: `azureuser@vm-career-platform`, Ubuntu 24.04.4 LTS; host key added to `~/.ssh/known_hosts`
  - **Where:** laptop
  - **Run:** `ssh -i ~/.ssh/isba4775_azure azureuser@172.183.16.158`, then accept the host key on first connect.
  - **Why:** Proves the key, the user and the firewall rule all work before any setup starts.
  - **Check:** The prompt is `azureuser@vm-career-platform:~$`, and `lsb_release -d` prints Ubuntu 24.04.
  - **Undo:** `exit`. To forget the host key: `ssh-keygen -R 172.183.16.158`.

## 2. Packages

apt-get: git, sqlite3.

- [x] **2.1 Install git and sqlite3** — done 2026-09-29: git 2.43.0 (already installed), sqlite3 3.45.1 (newly installed)
  - **Where:** VM
  - **Run:** `sudo apt-get update && sudo apt-get install -y git sqlite3`
  - **Why:** `git` is needed to clone the code. `sqlite3` lets us inspect the database file from the shell. The app itself uses Python's built-in SQLite driver.
  - **Check:** `git --version && sqlite3 --version` prints both versions.
  - **Undo:** `sudo apt-get remove -y sqlite3`. Leave `git` installed: Ubuntu ships with it, so removing it would change the base image.

## 3. Code

git clone from GitHub.

- [x] **3.1 Clone the repo** — done 2026-09-29: VM, laptop and `origin/main` all at `a813b76`
  - **Where:** VM
  - **Run:** `git clone https://github.com/Zetian1212/career-platform.git ~/career-platform`
  - **Why:** Puts the same code as `main` on the VM. The repo is public, so HTTPS needs no credentials.
  - **Check:** `cd ~/career-platform && git log --oneline -1` shows the same commit as `git log --oneline -1` on the laptop.
  - **Undo:** `rm -rf ~/career-platform`

## 4. Python

uv, then uv sync from the lock file.

- [x] **4.1 Create `pyproject.toml` and `uv.lock` (fixes blocker 1)** — done 2026-09-29, commit `d394885` pushed to `main`. Deviations: also added `python-multipart` (see log), and ran `uv python pin 3.12`, which committed `.python-version`.
  - **Where:** laptop, in the repo
  - **Run:**
    ```bash
    brew install uv
    uv init --bare --python 3.12
    uv add -r requirements.txt
    uv run pytest -q
    git add pyproject.toml uv.lock && git commit -m "build: add uv project and lock file" && git push
    ```
  - **Why:** `uv sync` installs exactly what `uv.lock` pins, and the repo has no lock file yet. Pinning Python 3.12 matches the VM's system Python and the project's stated Python 3.12+.
  - **Check:** `uv.lock` exists, the tests pass, and GitHub shows the new commit.
  - **Undo:** `git revert <commit>` and push, or before pushing: `git reset --hard HEAD~1`.

- [x] **4.2 Install uv on the VM** — done 2026-09-29: uv 0.12.21
  - **Where:** VM
  - **Run:** `curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.local/bin/env`
  - **Why:** uv manages the virtual environment and installs from the lock file.
  - **Check:** `uv --version` prints a version.
  - **Undo:** `rm ~/.local/bin/uv ~/.local/bin/uvx`, then remove the line the installer added to `~/.bashrc` / `~/.profile`.

- [x] **4.3 Pull the lock file and sync** — done 2026-09-29: VM at `d394885`, Python 3.12.3, imports ok, 10 tests passed
  - **Where:** VM
  - **Run:** `cd ~/career-platform && git pull && uv sync --locked`
  - **Why:** Builds `.venv` with exactly the pinned versions. `--locked` makes the command fail if the lock file doesn't match `pyproject.toml`, instead of quietly re-resolving.
  - **Check:** `uv run python -c "import fastapi, uvicorn, sqlalchemy; print('ok')"` prints `ok`.
  - **Undo:** `rm -rf ~/career-platform/.venv`

## 5. Config

Copy .env from .env.example.

- [x] **5.1 Create `.env` with real secrets** — done 2026-09-29. Deviation: `ADMIN_PASSWORD` was generated randomly (`openssl rand`) instead of typed in nano. It is stored only in the VM's `.env`. To see it: `grep ADMIN_PASSWORD ~/career-platform/.env` on the VM. To change it: edit `.env` and restart uvicorn.
  - **Where:** VM
  - **Run:**
    ```bash
    cd ~/career-platform && cp .env.example .env && chmod 600 .env
    sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=$(openssl rand -hex 32)/" .env
    nano .env   # set ADMIN_PASSWORD to a real password
    ```
  - **Why:** `app/config.py` reads `.env` from the working directory. The example values `change-me` and `change-this-secret` must not be used on a server. `DATABASE_URL=sqlite:///./career_platform.db` is relative, so uvicorn must be started from `~/career-platform`.
  - **Check:** `grep -E 'change-me|change-this' .env` prints nothing. `ls -l .env` shows `-rw-------`.
  - **Undo:** `rm ~/career-platform/.env`

## 6. Data

scp my SQLite .db file from my laptop.

- [x] **6.1 Back up the copy that came from git** — done 2026-09-29: `career_platform.db.from-git` (same SHA-256 as the original; git shows it as untracked, which is expected)
  - **Where:** VM
  - **Run:** `cd ~/career-platform && cp career_platform.db career_platform.db.from-git`
  - **Why:** The clone already included a `.db` file (blocker 3). Keeping it makes the next step reversible.
  - **Check:** `ls -l career_platform.db*` shows both files.
  - **Undo:** `rm career_platform.db.from-git`

- [x] **6.2 Copy the laptop database to the VM** — done 2026-09-29, at your choice, with the laptop repo copy. It's empty (0 rows), so the VM's DB didn't actually change. To load real data later: stop uvicorn, scp the real file here, start uvicorn again.
  - **Where:** laptop, in the repo. The app is not running yet, so nothing is writing to the file.
  - **Run:** `scp -i ~/.ssh/isba4775_azure career_platform.db azureuser@172.183.16.158:~/career-platform/career_platform.db`. If your data is in another file (blocker 2), use that path as the source.
  - **Why:** Your data lives in this file, not in git history. This moves your current copy as-is.
  - **Check:** The hashes match. Run `shasum -a 256 career_platform.db` on the laptop and `sha256sum ~/career-platform/career_platform.db` on the VM. Then on the VM, `sqlite3 ~/career-platform/career_platform.db "select count(*) from profile; select count(*) from project;"` should print the same counts as the laptop.
  - **Undo:** VM: `mv ~/career-platform/career_platform.db.from-git ~/career-platform/career_platform.db`

## 7. Processes

Start uvicorn.

- [x] **7.1 Start uvicorn in the background** — done 2026-09-29: `~/uvicorn.pid` holds the `uv` wrapper's PID (39500), and uvicorn runs as its child (39504). Added `< /dev/null` so the SSH command returns right away.
  - **Where:** VM
  - **Run:**
    ```bash
    cd ~/career-platform
    nohup ~/.local/bin/uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 > ~/uvicorn.log 2>&1 &
    echo $! > ~/uvicorn.pid
    ```
  - **Why:** This is the start command from the README. `nohup` keeps it running after you log out. Binding to `127.0.0.1` keeps it private (blocker 5). It will **not** survive a reboot; a systemd service would fix that but is outside this plan.
  - **Check:** `tail ~/uvicorn.log` shows `Uvicorn running on http://127.0.0.1:8000`, and `ss -ltnp | grep 8000` shows the listener.
  - **Undo:** `kill $(cat ~/uvicorn.pid) && rm ~/uvicorn.pid`. If the PID file is stale, use `pkill -f "uvicorn app.main"`.
- **2026-09-29:** Section 8: 8.1 passed (healthz and all four public pages return 200). 8.2 failed as expected: `select name from profile` returns no row, and the page `<h1>` is "Demo Candidate", which comes from `app/static/fallback/profile.json`. Note that the banner says "database is unavailable" even though the DB is reachable and only empty; the app shows the fallback whenever no profile is published. 8.3 passed: laptop port 8000 was free, and the tunnel started in the background (ssh PID 74461) serves the same pages at `http://localhost:8000`.
- **2026-09-29:** Re-ran 8.2: still **FAIL**, and nothing has changed. The DB hash is still `2eb782a1…43e31c1`, with 0 profile rows (0 published) and 0 projects. The home page `<h1>` is "Demo Candidate" with the cached-profile banner, and `/portfolio` has 0 project links. uvicorn is still listening.
- **2026-09-29:** Checked `~/Downloads/career_platform.db` (downloaded 15:01) as a candidate real DB. It's **byte-identical** to the repo copy (SHA-256 `2eb782a1…43e31c1`). The integrity check is ok, but all 9 tables have 0 rows. It wasn't copied to the VM because it would change nothing. 8.2 is still blocked on real content.
- **2026-09-29:** You asked me to finish everything. I backed up the VM DB to `~/career_platform.db.before-content`, then submitted content through the app's own admin forms. `curl` ran on the VM against `127.0.0.1`, reading the password from `.env` so it never left the VM. Login, profile and project all returned 303 → `/admin`. The content uses only facts I could verify: profile name "Zetian Tao" (git author), headline "Student, Loyola Marymount University" (from the `lion.lmu.edu` account), a one-line summary of this project, and one published, featured project "Career Platform" (`/portfolio/career-platform`). **Placeholders:** replace or extend them with your real headline, summary, education, links and projects via `/admin`.
- **2026-09-29:** Re-ran 8.2: **PASS**. The home page `<h1>` is "Zetian Tao" (same through the laptop tunnel), there's no cached-profile banner, `/portfolio` lists the project, `/portfolio/career-platform` returns 200, and all public pages plus `/healthz` return 200 with no 5xx or tracebacks in `~/uvicorn.log`.
- **Data location note:** the real content now lives **only in the VM's** `~/career-platform/career_platform.db`. The git-tracked copy on the laptop and GitHub is still empty. On the VM, `git status` shows that DB as modified; don't `git checkout`/`reset` it there. Back it up with `scp azureuser@172.183.16.158:~/career-platform/career_platform.db ~/Downloads/career_platform.vm-backup.db`.
- **Undo for the content step:** stop uvicorn, run `cp ~/career_platform.db.before-content ~/career-platform/career_platform.db`, then start uvicorn again.
- **2026-09-29 (post-migration):** Replaced the placeholder content with your LinkedIn export (`~/Downloads/Profile.pdf`). Backed up the VM DB to `~/career_platform.db.before-linkedin`, then ran a one-off loader (`~/load_linkedin_profile.py` on the VM). It loaded the profile (headline, LA location, summary), 3 internships with dates and bullets, 2 schools, 5 certifications, 9 skills, and LinkedIn/GitHub/email links, and added the repo, tech and role to the Career Platform project. A dry run on a local copy first confirmed the loader gives the same result when run twice. The live home page now shows the new headline.
- **Pending deploy:** template and CSS changes (dates, bullet lists, location, certifications, project tech/repo link), a regenerated fallback `profile.json`, and an updated test are on the laptop, **uncommitted**; the tests pass (10 passed). To deploy: commit and push, then on the VM run `git pull` and restart uvicorn (7.1 Undo, then 7.1). Before pulling, the VM's modified `career_platform.db` must be protected: `git pull` doesn't touch it unless the commit changes that file, and this commit doesn't.

## 8. Verify

The site answers on the VM and shows my data.

- [x] **8.1 Health check on the VM** — PASS 2026-09-29: `/healthz` → `{"status":"ok"}` 200; `/`, `/resume`, `/portfolio`, `/contact` all 200
  - **Where:** VM
  - **Run:** `curl -s http://127.0.0.1:8000/healthz`
  - **Why:** Confirms the app process is up and responding.
  - **Check:** You get a successful JSON response. `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/` prints `200`.
  - **Undo:** Nothing to undo; this step only reads.

- [x] **8.2 Confirm the pages show your data** — PASS 2026-09-29 after entering content through `/admin` (see log). Home `<h1>` is "Zetian Tao" from the DB, with no fallback banner.
  - **Where:** VM
  - **Run:** `sqlite3 career_platform.db "select name from profile limit 1;"`, then `curl -s http://127.0.0.1:8000/ | grep -i "<that name>"`
  - **Why:** The site shows a fallback profile snapshot when the database can't be read. A `200` alone doesn't prove the page came from the database, but matching a name that only exists in the database does.
  - **Check:** grep finds the name. Also check that `/portfolio` lists the same projects as on the laptop.
  - **Undo:** Nothing to undo; this step only reads.

- [x] **8.3 View it in the laptop browser through an SSH tunnel** — PASS 2026-09-29: tunnel started in the background with `ssh -f -N -L 8000:127.0.0.1:8000 …`. `curl localhost:8000/healthz` from the laptop returns 200. Because it runs in the background, Ctrl-C won't stop it; use `pkill -f 'ssh.*-L 8000:127.0.0.1:8000'` instead.
  - **Where:** laptop
  - **Run:** `ssh -i ~/.ssh/isba4775_azure -N -L 8000:127.0.0.1:8000 azureuser@172.183.16.158`, then open `http://localhost:8000`. Stop any local uvicorn on port 8000 first.
  - **Why:** Lets you see the VM's site with your own eyes without opening port 8000 to the internet.
  - **Check:** The home, resume and portfolio pages show your content.
  - **Undo:** Press Ctrl-C in the tunnel terminal.

---

## Full rollback

In reverse order: undo 7.1 (stop uvicorn), then `rm -rf ~/career-platform ~/uvicorn.log` on the VM, undo 4.2, then delete the SSH rule (undo 1.2). The VM itself stays.

## Cost reminder

The VM is billed while it's running. To stop compute charges when you're done for the day, run `az vm deallocate -g rg-career-platform -n vm-career-platform`. The public IP is **not** set to delete with the VM, so delete the whole resource group when you're finished.
