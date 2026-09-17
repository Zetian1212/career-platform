from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from app.repositories.content import ContentRepository


@dataclass
class LinkSnapshot:
    label: str
    url: str
    category: str | None = None


@dataclass
class SkillSnapshot:
    name: str
    category: str | None = None


@dataclass
class CoreProfileSnapshot:
    profile: dict
    links: list[LinkSnapshot] = field(default_factory=list)
    skills: list[SkillSnapshot] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _build_snapshot(session) -> CoreProfileSnapshot:
    repo = ContentRepository(session)
    profile = repo.get_profile()
    if profile is None:
        raise ValueError('No published profile found')
    links = [LinkSnapshot(label=l.label, url=l.url, category=l.category) for l in repo.get_links()]
    skills = [SkillSnapshot(name=s.name, category=s.category) for s in repo.list_skills()[:8]]
    projects = repo.list_projects()[:3]
    return CoreProfileSnapshot(
        profile={'name': profile.name, 'headline': profile.headline, 'summary': profile.summary, 'location': profile.location, 'availability': profile.availability, 'bio': profile.bio},
        links=links,
        skills=skills,
        highlights=[p.title for p in projects],
    )


def load_fallback_snapshot(path: str | Path) -> CoreProfileSnapshot:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    return CoreProfileSnapshot(
        profile=payload.get('profile', {}),
        links=[LinkSnapshot(**link) for link in payload.get('links', [])],
        skills=[SkillSnapshot(**skill) for skill in payload.get('skills', [])],
        highlights=list(payload.get('highlights', [])),
        generated_at=str(payload.get('generated_at', datetime.now(timezone.utc).isoformat())),
    )


def write_fallback_snapshot(snapshot: CoreProfileSnapshot, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'profile': snapshot.profile,
        'links': [
            {'label': link.get('label') if isinstance(link, dict) else link.label, 'url': link.get('url') if isinstance(link, dict) else link.url, 'category': (link.get('category') if isinstance(link, dict) else link.category)}
            for link in snapshot.links
        ],
        'skills': [
            {'name': skill.get('name') if isinstance(skill, dict) else skill.name, 'category': (skill.get('category') if isinstance(skill, dict) else skill.category)}
            for skill in snapshot.skills
        ],
        'highlights': snapshot.highlights,
        'generated_at': snapshot.generated_at,
    }
    target.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def get_profile_with_fallback(session_factory, snapshot_path: str | Path) -> tuple[CoreProfileSnapshot, bool]:
    try:
        session = session_factory()
        try:
            return _build_snapshot(session), False
        finally:
            session.close()
    except (SQLAlchemyError, ValueError, FileNotFoundError, OSError, RuntimeError):
        fallback = load_fallback_snapshot(snapshot_path)
        return fallback, True
