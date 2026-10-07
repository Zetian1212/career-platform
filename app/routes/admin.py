from __future__ import annotations
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.repositories.content import ContentRepository
from app.services.admin import is_authenticated, require_admin, _token

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')
settings = get_settings()


@router.get('/admin/login', response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse(request, 'admin/login.html', {'request': request, 'error': None})


@router.post('/admin/login')
def admin_login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username != settings.admin_username or password != settings.admin_password:
        return templates.TemplateResponse(request, 'admin/login.html', {'request': request, 'error': 'Invalid username or password'})
    response = RedirectResponse(url='/admin', status_code=303)
    response.set_cookie('admin_user', username, httponly=True)
    response.set_cookie('admin_session', _token(username), httponly=True)
    return response


@router.post('/admin/logout')
def admin_logout():
    response = RedirectResponse(url='/admin/login', status_code=303)
    response.delete_cookie('admin_user')
    response.delete_cookie('admin_session')
    return response


@router.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        require_admin(request)
    except PermissionError:
        return RedirectResponse(url='/admin/login', status_code=303)
    repo = ContentRepository(db)
    return templates.TemplateResponse(
        request,
        'admin/dashboard.html',
        {'profile': repo.get_profile(), 'projects': repo.list_projects(), 'experience': repo.list_experience(), 'skills': repo.list_skills()},
    )


@router.get('/admin/profile', response_class=HTMLResponse)
def admin_profile(request: Request, db: Session = Depends(get_db)):
    try:
        require_admin(request)
    except PermissionError:
        return RedirectResponse(url='/admin/login', status_code=303)
    repo = ContentRepository(db)
    return templates.TemplateResponse(request, 'admin/profile_form.html', {'profile': repo.get_profile()})


@router.post('/admin/profile')
def admin_profile_submit(request: Request, db: Session = Depends(get_db), name: str = Form(...), headline: str = Form(...), summary: str = Form(...), bio: str = Form('')):
    try:
        require_admin(request)
    except PermissionError:
        return RedirectResponse(url='/admin/login', status_code=303)
    repo = ContentRepository(db)
    profile = repo.get_profile()
    if profile is None:
        profile = repo.create_profile(name=name, headline=headline, summary=summary)
    else:
        profile.name = name
        profile.headline = headline
        profile.summary = summary
        profile.bio = bio.strip() or None
        db.commit()
    return RedirectResponse(url='/admin', status_code=303)


@router.get('/admin/projects/new', response_class=HTMLResponse)
def admin_project_new(request: Request):
    try:
        require_admin(request)
    except PermissionError:
        return RedirectResponse(url='/admin/login', status_code=303)
    return templates.TemplateResponse(request, 'admin/project_form.html', {'project': None})


@router.post('/admin/projects/new')
def admin_project_submit(request: Request, db: Session = Depends(get_db), title: str = Form(...), slug: str = Form(...), summary: str = Form(...), state: str = Form('draft'), featured: str = Form('false')):
    try:
        require_admin(request)
    except PermissionError:
        return RedirectResponse(url='/admin/login', status_code=303)
    repo = ContentRepository(db)
    repo.create_project(title=title, slug=slug or title.lower().replace(' ', '-'), summary=summary, state=state, featured=featured.lower() == 'true')
    return RedirectResponse(url='/admin', status_code=303)
