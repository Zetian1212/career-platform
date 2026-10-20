from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.repositories.content import ContentRepository
from app.services.profile import education_with_fallback, get_profile_with_fallback, load_interests
from app.static_version import static_version

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')
settings = get_settings()

SKILL_GROUPS = {'finance': 'Finance', 'tool': 'Technical', 'language': 'Technical', 'library': 'Technical', 'framework': 'Technical'}
SKILL_GROUP_ORDER = ['Finance', 'Technical']


def group_skills(skills) -> list[tuple[str, list]]:
    groups: dict[str, list] = {}
    for skill in skills:
        label = SKILL_GROUPS.get((skill.category or '').lower(), (skill.category or 'Other').title())
        groups.setdefault(label, []).append(skill)
    ranked = sorted(groups, key=lambda label: SKILL_GROUP_ORDER.index(label) if label in SKILL_GROUP_ORDER else len(SKILL_GROUP_ORDER))
    return [(label, groups[label]) for label in ranked]


def email_link(links):
    return next((link for link in links if link.url.startswith('mailto:')), None)


templates.env.globals.update(group_skills=group_skills, email_link=email_link, today=date.today, css_version=static_version('css/site.css'), js_version=static_version('js/analytics.js'), ga_measurement_id=settings.ga_measurement_id)


@router.get('/healthz')
def healthz():
    return {'status': 'ok'}


@router.get('/', response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    try:
        content = {'skills': repo.list_skills() or snapshot.skills, 'projects': repo.list_projects()[:3], 'education': education_with_fallback(repo, snapshot, settings.fallback_profile_path), 'experience': repo.list_experience()}
        status = 200
    except SQLAlchemyError:
        # Keep the profile up from the snapshot, but say so and return 503 rather than show stale or sample content.
        content = {'skills': snapshot.skills, 'projects': [], 'education': snapshot.education, 'experience': []}
        status = 503
    return templates.TemplateResponse(
        request,
        'public/home.html',
        {'profile': snapshot.profile, 'links': snapshot.links, **content, 'interests': load_interests(settings.fallback_profile_path), 'degraded': degraded, 'db_unavailable': status == 503},
        status_code=status,
    )


@router.get('/resume', response_class=HTMLResponse)
def resume(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    try:
        content = {'skills': repo.list_skills(), 'experience': repo.list_experience(), 'education': education_with_fallback(repo, snapshot, settings.fallback_profile_path), 'certifications': repo.list_certifications()}
        status = 200
    except SQLAlchemyError:
        content = {'skills': snapshot.skills, 'experience': [], 'education': snapshot.education, 'certifications': []}
        status = 503
    return templates.TemplateResponse(
        request,
        'public/resume.html',
        {'profile': snapshot.profile, 'links': snapshot.links, **content, 'degraded': degraded, 'db_unavailable': status == 503},
        status_code=status,
    )


def _projects_unavailable(request: Request, snapshot, degraded: bool):
    return templates.TemplateResponse(
        request,
        'public/portfolio.html',
        {'profile': snapshot.profile, 'projects': [], 'degraded': degraded, 'db_unavailable': True},
        status_code=503,
    )


@router.get('/portfolio', response_class=HTMLResponse)
def portfolio(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    try:
        projects = repo.list_projects()
    except SQLAlchemyError:
        return _projects_unavailable(request, snapshot, degraded)
    return templates.TemplateResponse(
        request,
        'public/portfolio.html',
        {'profile': snapshot.profile, 'projects': projects, 'degraded': degraded},
    )


@router.get('/portfolio/{slug}', response_class=HTMLResponse)
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    try:
        project = repo.get_project(slug)
    except SQLAlchemyError:
        return _projects_unavailable(request, snapshot, degraded)
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    return templates.TemplateResponse(
        request,
        'public/project.html',
        {'profile': snapshot.profile, 'project': project, 'degraded': degraded},
    )


@router.get('/contact', response_class=HTMLResponse)
def contact(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    return templates.TemplateResponse(
        request,
        'public/contact.html',
        {'profile': snapshot.profile, 'links': snapshot.links, 'degraded': degraded},
    )


@router.get('/privacy', response_class=HTMLResponse)
def privacy(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    return templates.TemplateResponse(
        request,
        'public/privacy.html',
        {'profile': snapshot.profile, 'degraded': degraded},
    )
