from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.repositories.content import ContentRepository
from app.services.profile import education_with_fallback, get_profile_with_fallback

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


templates.env.globals.update(group_skills=group_skills, email_link=email_link, today=date.today)


@router.get('/healthz')
def healthz():
    return {'status': 'ok'}


@router.get('/', response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    projects = repo.list_projects()[:3]
    return templates.TemplateResponse(
        request,
        'public/home.html',
        {'profile': snapshot.profile, 'links': snapshot.links, 'skills': snapshot.skills, 'projects': projects, 'education': education_with_fallback(repo, snapshot, settings.fallback_profile_path), 'degraded': degraded},
    )


@router.get('/resume', response_class=HTMLResponse)
def resume(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    return templates.TemplateResponse(
        request,
        'public/resume.html',
        {'profile': snapshot.profile, 'links': snapshot.links, 'skills': repo.list_skills(), 'experience': repo.list_experience(), 'education': education_with_fallback(repo, snapshot, settings.fallback_profile_path), 'certifications': repo.list_certifications(), 'degraded': degraded},
    )


@router.get('/portfolio', response_class=HTMLResponse)
def portfolio(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    return templates.TemplateResponse(
        request,
        'public/portfolio.html',
        {'profile': snapshot.profile, 'projects': repo.list_projects(), 'degraded': degraded},
    )


@router.get('/portfolio/{slug}', response_class=HTMLResponse)
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    project = repo.get_project(slug)
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
