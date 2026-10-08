from collections.abc import Generator
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def connect_args_for(url: str) -> dict:
    # check_same_thread is a sqlite3 option; psycopg rejects unknown arguments.
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


@lru_cache(maxsize=None)
def _engine_for(url: str):
    return create_engine(url, connect_args=connect_args_for(url), pool_pre_ping=True)


def get_engine():
    return _engine_for(get_settings().database_url)


def get_session_local():
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    from app.models import Profile, Experience, Education, Skill, Project, Certification, Link, MediaAsset  # noqa: F401
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
