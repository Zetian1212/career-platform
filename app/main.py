from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import get_settings
from app.db import init_db
from app.routes.public import router as public_router, templates as public_templates
from app.services.profile import load_fallback_snapshot
from app.routes.admin import router as admin_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(public_router)
    app.include_router(admin_router)

    @app.exception_handler(StarletteHTTPException)
    async def not_found_page(request: Request, exc: StarletteHTTPException):
        if exc.status_code != 404 or request.url.path.startswith(('/static/', '/healthz')):
            return await http_exception_handler(request, exc)
        try:
            profile = load_fallback_snapshot(settings.fallback_profile_path).profile
        except (OSError, ValueError):
            profile = None
        return public_templates.TemplateResponse(request, 'public/404.html', {'profile': profile}, status_code=404)
    init_db()
    return app


app = create_app()
