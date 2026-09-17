C# Personal Career Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a maintainable FastAPI/Jinja personal resume and portfolio site backed by SQLite, with structured editing, project impact storytelling, and a last-known-good profile snapshot that remains available when the database is unavailable.

**Architecture:** Use a server-rendered FastAPI application with Jinja templates and plain CSS. SQLModel/SQLAlchemy-style relational models will store structured career content in SQLite, while a small repository/service layer will keep database access separate from rendering. A generated JSON snapshot of the published core profile will be bundled with the application and used as an explicit fallback when SQLite cannot be read.

**Tech Stack:** Python 3.12+, FastAPI, Uvicorn, Jinja2, SQLModel, SQLite, Pydantic settings, pytest, httpx, and plain CSS. Development runs in GitHub Codespaces; deployment documentation targets an Azure VM running the same application behind a production process manager.

**Spec:** `docs/superpowers/specs/personal-career-platform.md`

## Global Constraints

- The public site uses FastAPI with server-rendered Jinja templates and plain CSS.
- SQLite is the v1 database and must be usable in Codespaces and on an Azure VM.
- The public profile must remain visible when the database is unavailable.
- Core fallback content must include identity, headline, summary, contact links, key skills, and a minimal project or experience summary.
- Content supports draft, review, published, archived, and featured states.
- Public content is database-backed during normal operation.
- No SPA framework or CSS framework is introduced.
- No implementation work begins until this plan is approved.

---

## File and module map

The greenfield repository will be organized as follows:

- `pyproject.toml`: Python package metadata, runtime dependencies, and test configuration.
- `.env.example`: documented local configuration values without secrets.
- `app/main.py`: FastAPI application factory, startup wiring, and route inclusion.
- `app/config.py`: typed environment configuration.
- `app/db.py`: SQLite engine, session dependency, and initialization hooks.
- `app/models.py`: relational content models and shared publishing-state types.
- `app/repositories/content.py`: read/write queries for published public content and admin operations.
- `app/services/profile.py`: published profile assembly and fallback snapshot generation/loading.
- `app/services/admin.py`: admin authentication and content mutation orchestration.
- `app/routes/public.py`: public homepage, resume, portfolio, project, and contact routes.
- `app/routes/admin.py`: authenticated admin pages and form handlers.
- `app/templates/base.html`: shared page shell and degraded-state indicator.
- `app/templates/public/*.html`: public page templates.
- `app/templates/admin/*.html`: admin forms and lists.
- `app/static/css/site.css`: responsive plain-CSS design system.
- `app/static/fallback/profile.json`: generated last-known-good core profile snapshot.
- `scripts/seed_demo.py`: deterministic local demo-content loader.
- `scripts/generate_snapshot.py`: explicit snapshot generation command.
- `tests/conftest.py`: isolated temporary SQLite fixtures and test client setup.
- `tests/test_public_routes.py`: public rendering and outage behavior.
- `tests/test_content_repository.py`: publishing and relationship query behavior.
- `tests/test_admin_routes.py`: authentication and structured editing behavior.
- `tests/test_snapshot.py`: snapshot generation and fallback behavior.
- `Dockerfile`: reproducible application image for local/Azure deployment.
- `docker-compose.yml`: optional local application invocation with a persistent SQLite volume.
- `docs/deployment/codespaces.md`: local Codespaces setup and checks.
- `docs/deployment/azure-vm.md`: Azure VM deployment and persistence guidance.

## Task 1: Scaffold the FastAPI application and test harness

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/config.py`
- Create: `app/routes/__init__.py`
- Create: `app/routes/public.py`
- Create: `app/templates/base.html`
- Create: `tests/conftest.py`
- Create: `tests/test_public_routes.py`
- Create: `.env.example`

**Interfaces:**
- `create_app() -> FastAPI` in `app/main.py`
- `get_settings() -> Settings` in `app/config.py`
- `GET /healthz -> {"status": "ok"}` for deployment checks
- `GET / -> HTMLResponse` with a temporary, explicit empty-profile state

- [ ] **Step 1: Write the failing smoke test**

```python
def test_health_endpoint_returns_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_public_routes.py::test_health_endpoint_returns_ok -q`

Expected: FAIL because the application package and health route do not exist.

- [ ] **Step 3: Add the application scaffold**

Implement `create_app()`, typed settings, Jinja template loading, the health
route, and a test client fixture using `httpx.AsyncClient` or the repository's
chosen compatible FastAPI test-client pattern. Keep configuration sourced from
environment variables with safe local defaults.

- [ ] **Step 4: Run the smoke test**

Run: `pytest tests/test_public_routes.py::test_health_endpoint_returns_ok -q`

Expected: PASS.

**Done looks like:** A clean checkout can install the declared dependencies,
start FastAPI, answer `/healthz`, and render a base HTML document without a
database connection.

**How to check:** Run `python -m uvicorn app.main:create_app --factory --reload`
and request `http://127.0.0.1:8000/healthz`; then run the targeted pytest command.

## Task 2: Add the SQLite schema and content repository

**Files:**
- Create: `app/db.py`
- Create: `app/models.py`
- Create: `app/repositories/__init__.py`
- Create: `app/repositories/content.py`
- Create: `tests/test_content_repository.py`
- Modify: `app/main.py`
- Modify: `tests/conftest.py`

**Interfaces:**
- `get_session() -> Iterator[Session]`
- `init_db() -> None`
- `PublishedProfileRepository.get_profile() -> Profile | None`
- `PublishedProfileRepository.list_experience() -> list[Experience]`
- `PublishedProfileRepository.list_projects() -> list[Project]`
- `PublishedProfileRepository.list_skills() -> list[Skill]`
- `ContentRepository.save_profile(...) -> Profile`
- Shared enum `PublishState = draft | review | published | archived`

- [ ] **Step 1: Write repository tests**

```python
def test_only_published_projects_are_visible(repository):
    repository.create_project(title="Draft", state="draft")
    repository.create_project(title="Live", state="published")

    projects = repository.list_projects()

    assert [project.title for project in projects] == ["Live"]
```

```python
def test_featured_project_is_ordered_first(repository):
    repository.create_project(title="Other", state="published", featured=False)
    repository.create_project(title="Featured", state="published", featured=True)

    projects = repository.list_projects()

    assert projects[0].title == "Featured"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_content_repository.py -q`

Expected: FAIL because models, database setup, and repository methods do not
exist.

- [ ] **Step 3: Implement the relational model**

Create tables for `Profile`, `Experience`, `Education`, `Skill`, `Project`,
`Certification`, `Link`, and `MediaAsset`, plus project-skill and
project-experience relationships. Add `state`, `featured`, `sort_order`,
created/updated timestamps, and required public fields. Use foreign keys and
relationship declarations rather than storing relationship IDs in free-form
JSON.

- [ ] **Step 4: Implement the repository**

Implement parameterized queries that return only published records for public
read methods, with deterministic ordering: featured first, then explicit
`sort_order`, then newest update. Keep write methods separate so public routes
cannot accidentally mutate content.

- [ ] **Step 5: Run the repository tests**

Run: `pytest tests/test_content_repository.py -q`

Expected: PASS.

**Done looks like:** A temporary SQLite database can be initialized, seeded
with records in every publishing state, and queried through typed repository
methods without exposing drafts to public reads.

**How to check:** Run `pytest tests/test_content_repository.py -q` and inspect
the generated SQLite schema with `sqlite3` or the project's migration command.

## Task 3: Build the published profile service and outage snapshot

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/profile.py`
- Create: `app/static/fallback/profile.json`
- Create: `scripts/generate_snapshot.py`
- Create: `tests/test_snapshot.py`
- Modify: `app/repositories/content.py`
- Modify: `app/config.py`

**Interfaces:**
- `CoreProfileSnapshot` with `profile`, `links`, `skills`, `highlights`, and `generated_at`
- `load_published_profile(session) -> CoreProfileSnapshot`
- `load_fallback_snapshot(path) -> CoreProfileSnapshot`
- `get_profile_with_fallback(session_factory, snapshot_path) -> tuple[CoreProfileSnapshot, bool]`
- `write_fallback_snapshot(snapshot, path) -> None`

- [ ] **Step 1: Write outage and snapshot tests**

```python
def test_profile_uses_snapshot_when_database_connection_fails(snapshot_path):
    profile, degraded = get_profile_with_fallback(
        session_factory=raising_session_factory,
        snapshot_path=snapshot_path,
    )

    assert degraded is True
    assert profile.profile.name == "Demo Candidate"
    assert profile.links[0].url.startswith("https://")
```

```python
def test_snapshot_contains_only_core_public_fields(published_database, snapshot_path):
    snapshot = load_published_profile(published_database)
    write_fallback_snapshot(snapshot, snapshot_path)
    payload = json.loads(snapshot_path.read_text())

    assert set(payload) == {"profile", "links", "skills", "highlights", "generated_at"}
    assert "database_password" not in json.dumps(payload)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_snapshot.py -q`

Expected: FAIL because the snapshot service and fallback file do not exist.

- [ ] **Step 3: Implement the snapshot service**

Assemble the minimum required public fields from published records. On database
read errors, load and validate the bundled JSON snapshot instead of returning
an empty success response. Return an explicit `degraded` flag so templates can
show a last-updated or temporary-unavailability message. Do not catch broad
exceptions; catch the database/validation errors expected from the configured
session and snapshot parser, and re-raise if the snapshot is also invalid.

- [ ] **Step 4: Implement snapshot generation**

Make `python scripts/generate_snapshot.py` initialize the configured database,
read published content, validate the exact snapshot schema, and write
`app/static/fallback/profile.json` atomically. The command must fail non-zero if
there is no valid published profile.

- [ ] **Step 5: Run the snapshot tests**

Run: `pytest tests/test_snapshot.py -q`

Expected: PASS.

**Done looks like:** The core profile renders from the database during normal
operation and from the bundled snapshot during a simulated SQLite failure,
with the degraded state distinguishable to the presentation layer.

**How to check:** Run the snapshot tests, temporarily point the app at an
unavailable SQLite path, request `/`, and verify identity, summary, links,
skills, and highlights remain visible with a degraded-state indicator.

## Task 4: Add public resume and portfolio routes

**Files:**
- Modify: `app/routes/public.py`
- Modify: `app/templates/base.html`
- Create: `app/templates/public/home.html`
- Create: `app/templates/public/resume.html`
- Create: `app/templates/public/portfolio.html`
- Create: `app/templates/public/project.html`
- Create: `app/templates/public/contact.html`
- Modify: `tests/test_public_routes.py`

**Interfaces:**
- `GET / -> HTMLResponse`
- `GET /resume -> HTMLResponse`
- `GET /portfolio -> HTMLResponse`
- `GET /portfolio/{project_slug} -> HTMLResponse`
- `GET /contact -> HTMLResponse`
- Templates receive `profile`, `experience`, `education`, `skills`, `projects`,
  `links`, and `degraded`

- [ ] **Step 1: Write route rendering tests**

```python
def test_homepage_renders_published_profile(client, seeded_database):
    response = client.get("/")

    assert response.status_code == 200
    assert "Demo Candidate" in response.text
    assert "Measured impact" in response.text
    assert "Draft project" not in response.text
```

```python
def test_homepage_shows_degraded_indicator_when_database_is_unavailable(
    client_with_unavailable_database,
):
    response = client_with_unavailable_database.get("/")

    assert response.status_code == 200
    assert "cached profile" in response.text.lower()
    assert "Demo Candidate" in response.text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_public_routes.py -q`

Expected: FAIL because the public routes and templates are incomplete.

- [ ] **Step 3: Implement the route handlers**

Use the profile service for every public request. Return `404` for an
unpublished or unknown project slug, and preserve the shared site shell for
non-core content failures. Pass an explicit degraded flag to every template.

- [ ] **Step 4: Implement semantic templates**

Create accessible headings, navigation, skip link, contact links, project
case-study sections for problem/approach/outcome, and a visible but concise
degraded-state banner. Do not expose draft or archived records.

- [ ] **Step 5: Run public route tests**

Run: `pytest tests/test_public_routes.py -q`

Expected: PASS.

**Done looks like:** A visitor can navigate profile, resume, portfolio,
project, and contact pages; project pages show evidence and outcomes; the
homepage remains useful and honest during an outage.

**How to check:** Run the targeted tests, start Uvicorn, and manually visit
`/`, `/resume`, `/portfolio`, and a published project URL at desktop and mobile
widths.

## Task 5: Add authenticated structured admin editing

**Files:**
- Create: `app/services/admin.py`
- Modify: `app/routes/admin.py`
- Create: `app/templates/admin/login.html`
- Create: `app/templates/admin/dashboard.html`
- Create: `app/templates/admin/profile_form.html`
- Create: `app/templates/admin/project_form.html`
- Create: `app/templates/admin/experience_form.html`
- Create: `app/templates/admin/skill_form.html`
- Create: `tests/test_admin_routes.py`
- Modify: `app/config.py`
- Modify: `app/main.py`

**Interfaces:**
- `POST /admin/login -> RedirectResponse`
- `POST /admin/logout -> RedirectResponse`
- `GET /admin -> HTMLResponse`
- `GET|POST /admin/profile -> HTMLResponse | RedirectResponse`
- `GET|POST /admin/projects/new -> HTMLResponse | RedirectResponse`
- `GET|POST /admin/experience/new -> HTMLResponse | RedirectResponse`
- `GET|POST /admin/skills/new -> HTMLResponse | RedirectResponse`
- `require_admin(request) -> None`

- [ ] **Step 1: Write authentication and mutation tests**

```python
def test_admin_dashboard_requires_authentication(client):
    response = client.get("/admin", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
```

```python
def test_authenticated_admin_can_create_draft_project(authenticated_client):
    response = authenticated_client.post(
        "/admin/projects/new",
        data={"title": "New project", "state": "draft", "outcomes": "10% faster"},
    )

    assert response.status_code == 303
    assert "New project" in authenticated_client.get("/admin").text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_admin_routes.py -q`

Expected: FAIL because admin routes, session handling, and forms do not exist.

- [ ] **Step 3: Implement authentication**

Use an environment-provided password hash and signed, secure session cookie.
Protect every admin route with `require_admin`; do not place credentials in
SQLite or templates. Set secure cookie behavior appropriate to local HTTP and
document the production override.

- [ ] **Step 4: Implement structured forms**

Provide forms for profile, experience, projects, and skills. Validate required
fields with Pydantic/form schemas, preserve publishing state transitions, and
redirect after successful writes to prevent duplicate submissions. Return
field-level errors without swallowing database errors.

- [ ] **Step 5: Run admin tests**

Run: `pytest tests/test_admin_routes.py -q`

Expected: PASS.

**Done looks like:** The owner can sign in, create/update structured content,
save drafts, publish selected content, and log out; unauthenticated visitors
cannot access mutation routes.

**How to check:** Run the admin tests, set a local admin password hash, sign in
at `/admin/login`, create a draft project, publish it, and confirm it appears
on the public portfolio only after publication.

## Task 6: Implement the visual system and responsive accessibility

**Files:**
- Create: `app/static/css/site.css`
- Create: `tests/test_accessibility_contract.py`
- Modify: `app/templates/base.html`
- Modify: `app/templates/public/*.html`
- Modify: `app/templates/admin/*.html`

**Interfaces:**
- Shared CSS custom properties for color, typography, spacing, and layout.
- Shared template blocks for title, navigation, main content, and status banner.

- [ ] **Step 1: Write HTML contract tests**

```python
def test_public_pages_have_title_main_and_navigation(client):
    for path in ["/", "/resume", "/portfolio", "/contact"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "<title>" in response.text
        assert "<main" in response.text
        assert 'aria-label="Primary navigation"' in response.text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_accessibility_contract.py -q`

Expected: FAIL until all templates use the shared semantic shell.

- [ ] **Step 3: Implement plain CSS**

Add responsive layout primitives, readable typography, visible keyboard focus,
contrast-safe colors, reduced-motion behavior, card/case-study layouts, and
mobile navigation that works without JavaScript.

- [ ] **Step 4: Run the accessibility contract test**

Run: `pytest tests/test_accessibility_contract.py -q`

Expected: PASS.

**Done looks like:** The public and admin pages share a coherent responsive
visual language, remain usable without JavaScript, and expose semantic landmarks
and keyboard focus.

**How to check:** Run the contract test and manually inspect the public pages
at 375px and 1440px widths with keyboard-only navigation.

## Task 7: Add deterministic seed data and snapshot workflow

**Files:**
- Create: `scripts/seed_demo.py`
- Modify: `scripts/generate_snapshot.py`
- Create: `tests/test_seed_workflow.py`
- Modify: `.env.example`
- Modify: `README.md`

**Interfaces:**
- `python scripts/seed_demo.py --reset`
- `python scripts/generate_snapshot.py`
- Seed command creates a known demo profile, experience, education, skills,
  projects, certifications, links, and media records.

- [ ] **Step 1: Write workflow tests**

```python
def test_seed_is_repeatable(tmp_path):
    run_seed(database_path=tmp_path / "career.db", reset=True)
    first = read_public_counts(tmp_path / "career.db")
    run_seed(database_path=tmp_path / "career.db", reset=False)
    second = read_public_counts(tmp_path / "career.db")

    assert first == second
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_seed_workflow.py -q`

Expected: FAIL because the seed workflow does not exist.

- [ ] **Step 3: Implement deterministic seed and snapshot commands**

Use stable slugs and values, make `--reset` explicit before deleting local
content, and ensure the generated snapshot is derived only from published
records. Document how to replace demo data with the owner's content.

- [ ] **Step 4: Run workflow tests**

Run: `pytest tests/test_seed_workflow.py -q`

Expected: PASS.

**Done looks like:** A new developer can create a usable local site with one
documented command, regenerate the fallback snapshot, and repeat the process
without duplicate records.

**How to check:** Run the seed and snapshot commands in a temporary directory,
start the app, and verify the same content appears in the public pages.

## Task 8: Package and document Codespaces and Azure VM deployment

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `docs/deployment/codespaces.md`
- Create: `docs/deployment/azure-vm.md`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Create: `tests/test_deployment_contract.py`

**Interfaces:**
- Container starts with `uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000`.
- `GET /healthz` is the deployment readiness check.
- SQLite database path and admin configuration are supplied through environment
  variables.

- [ ] **Step 1: Write deployment contract tests**

```python
def test_production_start_command_is_documented():
    text = Path("docs/deployment/azure-vm.md").read_text()
    assert "uvicorn app.main:create_app --factory" in text
    assert "/healthz" in text
    assert "SQLite" in text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_deployment_contract.py -q`

Expected: FAIL because deployment documentation and container files do not
exist.

- [ ] **Step 3: Add packaging and persistence configuration**

Create a non-root container image, expose port 8000, mount a persistent
directory for SQLite, and configure the application to trust only explicit
environment values. Document Codespaces port forwarding and Azure VM disk
backup/permission requirements.

- [ ] **Step 4: Run deployment checks**

Run: `pytest tests/test_deployment_contract.py -q`

Expected: PASS.

**Done looks like:** The application can run locally in Codespaces with
persistent SQLite storage and has a reproducible Azure VM deployment procedure
with health checking and database backup guidance.

**How to check:** Build and run the container, request `/healthz`, create
content, restart the container with the SQLite volume preserved, and verify the
content and fallback snapshot remain available.

## Task 9: Run the complete verification suite and document release checks

**Files:**
- Modify: `README.md`
- Create: `docs/verification/release-checklist.md`

- [ ] **Step 1: Run the complete test suite**

Run: `pytest -q`

Expected: PASS with all route, repository, snapshot, admin, accessibility,
workflow, and deployment-contract tests green.

- [ ] **Step 2: Run the production-like smoke check**

Run:

```bash
python scripts/seed_demo.py --reset
python scripts/generate_snapshot.py
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Check `/healthz`, `/`, `/resume`, `/portfolio`, `/admin/login`, and a published
project URL. Then make the SQLite path unavailable and confirm `/` still
renders the snapshot with a degraded-state indicator.

- [ ] **Step 3: Record the release checklist**

Document dependency installation, seed/snapshot commands, admin secret setup,
database backup, outage simulation, and the exact commands above.

**Done looks like:** The repository has a repeatable test and smoke-check
procedure that proves normal database rendering, content editing, and
database-outage profile visibility before deployment.

**How to check:** Run `pytest -q` and complete every item in
`docs/verification/release-checklist.md`.

---

## Plan self-review

### Spec coverage

- Product goal and early-career audience: Tasks 2, 4, and 6.
- Proof-oriented project storytelling: Tasks 2 and 4.
- Structured database content and relationships: Task 2.
- Draft/review/published/archived/featured lifecycle: Tasks 2 and 5.
- Graceful degradation and last-known-good snapshot: Task 3 and Task 4.
- Responsive, accessible public site: Task 6.
- Future extensibility through separated repositories, services, and templates:
  Tasks 1 through 5.
- Codespaces and Azure VM deployment: Task 8.
- Maintainability and owner editing workflow: Tasks 5 and 7.

### Placeholder scan

No implementation steps depend on TBD values or unspecified interfaces. The
only runtime values that must be supplied by deployment are documented
environment variables for the SQLite path, session secret, and admin password
hash.

### Type/interface consistency

The profile snapshot type produced by `app/services/profile.py` is consumed by
public routes and the fallback generator. Repository methods use the same
publishing-state enum and entity names across Tasks 2 through 5.
