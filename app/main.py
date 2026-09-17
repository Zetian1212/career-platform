from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.db import init_db
from app.routes.public import router as public_router
from app.routes.admin import router as admin_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(public_router)
    app.include_router(admin_router)
    init_db()
    return app


app = create_app()
