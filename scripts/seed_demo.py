from __future__ import annotations
import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import Base, connect_args_for
from app.models import Profile, Link, Skill, Project


def seed_demo(reset: bool = False) -> None:
    settings = get_settings()
    if not settings.database_url.startswith('sqlite'):
        raise SystemExit('seed_demo only writes to local SQLite files; refusing to touch ' + settings.database_url.split('@')[-1])
    database_path = Path.cwd() / settings.database_url.replace('sqlite:///./', '')
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.database_url, connect_args=connect_args_for(settings.database_url))
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        if session.query(Profile).count() == 0:
            profile = Profile(name='Demo Candidate', headline='Full-Stack Product Engineer', summary='I build reliable products that turn complexity into measurable value.', location='Remote', availability='Open to opportunities', bio='Career-focused product engineer.', state='published')
            session.add(profile)
            session.flush()
            session.add_all([
                Link(label='LinkedIn', url='https://www.linkedin.com/in/demo-candidate', category='social', profile_id=profile.id, sort_order=1),
                Link(label='GitHub', url='https://github.com/demo-candidate', category='code', profile_id=profile.id, sort_order=2),
            ])
            skill = Skill(name='Python', category='language', state='published', sort_order=1)
            skill2 = Skill(name='FastAPI', category='framework', state='published', sort_order=2)
            session.add_all([skill, skill2])
            session.flush()
            project = Project(title='Workflow Automation Platform', slug='workflow-automation-platform', summary='Automated repetitive work for product teams.', problem='Manual coordination slowed delivery.', impact='Reduced coordination time by 40%.', state='published', featured=True, technology='Python, FastAPI, SQLite', sort_order=1)
            project.skills.extend([skill, skill2])
            session.add(project)
            session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    seed_demo(reset=args.reset)
