# Personal Career Platform Specification

This document records the approved product direction for the career platform.

## Goals
- Build a database-driven resume and portfolio website.
- Keep the public profile visible when the database is unavailable.
- Support future growth into a broader career platform.

## Architecture
- FastAPI + Jinja templates + plain CSS
- SQLite for v1
- Structured content stored in a relational database
- Last-known-good fallback snapshot for core profile visibility
