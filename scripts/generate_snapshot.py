from app.config import get_settings
from app.db import Base, get_engine
from sqlalchemy.orm import Session
from app.services.profile import _build_snapshot, write_fallback_snapshot


def generate_snapshot() -> None:
    settings = get_settings()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        snapshot = _build_snapshot(session)
        write_fallback_snapshot(snapshot, settings.fallback_profile_path)
        print(f'Snapshot generated: {settings.fallback_profile_path}')


if __name__ == '__main__':
    generate_snapshot()
