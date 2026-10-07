from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
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
class EducationSnapshot:
    school: str
    degree: str
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    honors: str | None = None


def _month(value: str | None) -> date | None:
    if not value:
        return None
    year, month = value.split('-')[:2]
    return date(int(year), int(month), 1)


def _education_payload(item) -> dict:
    return {
        'school': item.school,
        'degree': item.degree,
        'field_of_study': item.field_of_study,
        'start_date': item.start_date.strftime('%Y-%m') if item.start_date else None,
        'end_date': item.end_date.strftime('%Y-%m') if item.end_date else None,
        'honors': item.honors,
    }


@dataclass
class CoreProfileSnapshot:
    profile: dict
    links: list[LinkSnapshot] = field(default_factory=list)
    skills: list[SkillSnapshot] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    education: list[EducationSnapshot] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _build_snapshot(session) -> CoreProfileSnapshot:
    repo = ContentRepository(session)
    profile = repo.get_profile()
    if profile is None:
        raise ValueError('No published profile found')
    links = [LinkSnapshot(label=l.label, url=l.url, category=l.category) for l in repo.get_links()]
    skills = [SkillSnapshot(name=s.name, category=s.category) for s in repo.list_skills()[:8]]
    projects = repo.list_projects()[:3]
    education = [
        EducationSnapshot(school=e.school, degree=e.degree, field_of_study=e.field_of_study, start_date=e.start_date, end_date=e.end_date, honors=e.honors)
        for e in repo.list_education()
    ]
    return CoreProfileSnapshot(
        profile={'name': profile.name, 'headline': profile.headline, 'summary': profile.summary, 'location': profile.location, 'availability': profile.availability, 'bio': profile.bio},
        links=links,
        skills=skills,
        highlights=[p.title for p in projects],
        education=education,
    )


def load_fallback_snapshot(path: str | Path) -> CoreProfileSnapshot:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    return CoreProfileSnapshot(
        profile=payload.get('profile', {}),
        links=[LinkSnapshot(**link) for link in payload.get('links', [])],
        skills=[SkillSnapshot(**skill) for skill in payload.get('skills', [])],
        highlights=list(payload.get('highlights', [])),
        education=[
            EducationSnapshot(**{**item, 'start_date': _month(item.get('start_date')), 'end_date': _month(item.get('end_date'))})
            for item in payload.get('education', [])
        ],
        generated_at=str(payload.get('generated_at', datetime.now(timezone.utc).isoformat())),
    )


def write_fallback_snapshot(snapshot: CoreProfileSnapshot, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    education = [_education_payload(item) for item in snapshot.education]
    if not education:
        # Keep the committed education record when the database has none yet.
        education = existing.get('education', [])
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
        'education': education,
        'generated_at': snapshot.generated_at,
    }
    if existing.get('interests'):
        # Interests are edited in the file itself, not in the database.
        payload['interests'] = existing['interests']
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


def education_with_fallback(repo, snapshot: CoreProfileSnapshot, snapshot_path: str | Path) -> list:
    rows = repo.list_education()
    if rows:
        return rows
    if snapshot.education:
        return snapshot.education
    try:
        return load_fallback_snapshot(snapshot_path).education
    except (OSError, ValueError, TypeError):
        return []


def load_interests(snapshot_path: str | Path) -> list[str]:
    try:
        payload = json.loads(Path(snapshot_path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return [str(item) for item in payload.get('interests', []) if str(item).strip()]
