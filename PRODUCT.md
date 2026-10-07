# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Recruiters across finance and technology: finance roles (equity research, corporate finance, due diligence) and tech/data roles (business analysis, information systems, fintech). They arrive from a LinkedIn profile, a resume link, or an application, and they have a short time to decide whether to reach out. The candidate (Zetian Tao) is the secondary user and maintains the content through the admin area.

## Product Purpose

A personal resume and portfolio site for Zetian Tao, a BBA student at Loyola Marymount University (Finance + Information Systems and Business Analysis, expected June 2027). It presents the profile, resume, skills, projects, and contact links so a recruiter can judge fit quickly and get in touch. Success means a recruiter understands the candidate's profile in one visit and has an obvious way to make contact (email, LinkedIn) or read the resume.

The site also serves as a Cloud Computing course project, deployed on an Azure VM. That is part of its operating context, not its main audience.

## Positioning

A finance + tech hybrid: a finance student who also builds, deploys, and operates real software. The site itself is evidence of the technical side, because it is database-driven, self-hosted on Azure, and stays available when its database is not. Finance skills (DCF, comps, equity research, due diligence) and technical skills (Python, pandas, cloud deployment) should both read as first-class, not one as a footnote to the other.

## Operating Context

- Public pages: Home, Resume, Portfolio (with project detail pages), Contact.
- Admin area (`/admin`): login, dashboard, profile and project editing. Used only by the candidate.
- Content comes from a relational database (SQLite in v1). A last-known-good snapshot (`app/static/fallback/profile.json`) keeps the core profile visible when the database is unavailable, and the site then shows a "cached profile" status banner.
- Deployed on an Azure VM; `/healthz` reports liveness.

## Capabilities and Constraints

- Current implementation: FastAPI + Jinja templates + plain CSS, server-rendered. The user did not lock this stack; it describes the incumbent, not a requirement.
- Degraded mode and the test contracts (primary navigation, `<main>`, skip link) exist today. They weren't declared binding, but changing them means updating the tests deliberately.
- **Binding: real content only.** Never invent projects, metrics, employers, roles, testimonials, or outcomes. Content must come from `Profile.pdf` or the database.
- Undecided: whether the resume is offered as a downloadable file.

## Evidence on Hand

- `Profile.pdf`: source profile (LinkedIn export).
- `app/static/fallback/profile.json`: real name, headline, summary, location, links (LinkedIn, GitHub, email), and skills (DCF modeling, comparable company analysis, equity research, financial due diligence, Excel, Bloomberg, Python, pandas).
- The career platform itself (this repo and its Azure deployment) is the one real project so far.
- **Absent:** no real portfolio projects are in the database yet, and there are no testimonials, quantified outcomes, or employer logos. `scripts/seed_demo.py` contains placeholder data ("Demo Candidate", a "40%" impact figure) for development only; it must never appear as real content or as a design sample.

## Product Principles

1. Truth over polish: an empty section is better than an invented one.
2. Both halves count: finance depth and technical ability get equal weight.
3. Fast to judge: a recruiter should grasp who this is and how to reach them within one screen.
4. The site is part of the proof: reliability and craft in the site itself support the technical claim.
5. Always reachable: the core profile and contact routes stay visible even when parts of the system fail.
