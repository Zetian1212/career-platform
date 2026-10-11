import os
from datetime import date
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from app.db import Base
from app.models import Experience, Profile, Project, Skill
from scripts.copy_sqlite_to_postgres import copy_database


def _source(tmp_path):
    url = f'sqlite:///{tmp_path / "source.db"}'
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        profile = Profile(name='Zetian Tao', headline='h', summary='s')
        s.add(profile)
        s.flush()
        s.add(Experience(role='Intern', company='Co', start_date=date(2025, 7, 1), profile_id=profile.id))
        skill = Skill(name='Python')
        project = Project(title='Career Platform', slug='career-platform', summary='s', featured=True)
        project.skills.append(skill)
        s.add_all([skill, project])
        s.commit()
    return url


def test_copy_preserves_rows_types_and_links(tmp_path):
    target = f'sqlite:///{tmp_path / "target.db"}'
    counts = copy_database(_source(tmp_path), target)
    assert counts['profile'] == 1 and counts['project_skill'] == 1
    with Session(create_engine(target)) as s:
        assert s.scalar(select(Experience.start_date)) == date(2025, 7, 1)
        assert s.scalar(select(Project.featured)) is True
        assert s.get(Project, 1).skills[0].name == 'Python'


def test_copy_refuses_non_empty_target(tmp_path):
    source = _source(tmp_path)
    target = f'sqlite:///{tmp_path / "target.db"}'
    copy_database(source, target)
    with pytest.raises(SystemExit):
        copy_database(source, target)


@pytest.mark.skipif('TEST_POSTGRES_URL' not in os.environ, reason='needs a throwaway Postgres')
def test_copy_into_postgres_then_insert(tmp_path):
    url = os.environ['TEST_POSTGRES_URL']
    assert url.rsplit('/', 1)[-1].endswith('_test'), 'refusing: database name must end in _test'
    engine = create_engine(url.replace('postgresql://', 'postgresql+psycopg://', 1))
    Base.metadata.drop_all(engine)
    try:
        copy_database(_source(tmp_path), url)
        with Session(engine) as s:
            # Fails with a duplicate key unless the id sequences were reset.
            s.add(Project(title='New', slug='new', summary='s'))
            s.commit()
            assert s.scalar(select(func.max(Project.id))) == 2
    finally:
        Base.metadata.drop_all(engine)
