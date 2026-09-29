from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.repositories.content import ContentRepository
from app.services.profile import get_profile_with_fallback

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')
settings = get_settings()


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
        {'profile': snapshot.profile, 'links': snapshot.links, 'skills': snapshot.skills, 'projects': projects, 'degraded': degraded},
    )


@router.get('/resume', response_class=HTMLResponse)
def resume(request: Request, db: Session = Depends(get_db)):
    snapshot, degraded = get_profile_with_fallback(lambda: db, settings.fallback_profile_path)
    repo = ContentRepository(db)
    return templates.TemplateResponse(
        request,
        'public/resume.html',
        {'profile': snapshot.profile, 'links': snapshot.links, 'skills': repo.list_skills(), 'experience': repo.list_experience(), 'education': repo.list_education(), 'certifications': repo.list_certifications(), 'degraded': degraded},
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
        {'profile': snapshot.profile, 'links': repo.get_links(), 'degraded': degraded},
    )
