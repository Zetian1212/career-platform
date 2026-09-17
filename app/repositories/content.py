from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Profile, Link, Skill, Experience, Education, Certification, Project


class ContentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_profile(self) -> Profile | None:
        return self.session.execute(select(Profile).where(Profile.state == 'published')).scalars().first()

    def get_links(self) -> list[Link]:
        profile = self.get_profile()
        if profile is None:
            return []
        return self.session.execute(
            select(Link).where(Link.profile_id == profile.id).order_by(Link.sort_order, Link.id)
        ).scalars().all()

    def list_skills(self) -> list[Skill]:
        return self.session.execute(
            select(Skill).where(Skill.state == 'published').order_by(Skill.sort_order, Skill.name)
        ).scalars().all()

    def list_experience(self) -> list[Experience]:
        profile = self.get_profile()
        if profile is None:
            return []
        return self.session.execute(
            select(Experience).where(Experience.profile_id == profile.id, Experience.state == 'published').order_by(Experience.sort_order.desc(), Experience.id)
        ).scalars().all()

    def list_education(self) -> list[Education]:
        profile = self.get_profile()
        if profile is None:
            return []
        return self.session.execute(
            select(Education).where(Education.profile_id == profile.id, Education.state == 'published').order_by(Education.sort_order.desc(), Education.id)
        ).scalars().all()

    def list_certifications(self) -> list[Certification]:
        profile = self.get_profile()
        if profile is None:
            return []
        return self.session.execute(
            select(Certification).where(Certification.profile_id == profile.id, Certification.state == 'published').order_by(Certification.issued_date.desc().nullslast(), Certification.id)
        ).scalars().all()

    def list_projects(self) -> list[Project]:
        return self.session.execute(
            select(Project).where(Project.state == 'published').order_by(Project.featured.desc(), Project.sort_order, Project.updated_at.desc())
        ).scalars().all()

    def get_project(self, slug: str) -> Project | None:
        return self.session.execute(
            select(Project).where(Project.slug == slug, Project.state == 'published')
        ).scalars().first()

    def create_profile(self, *, name: str, headline: str, summary: str, location: str | None = None, availability: str | None = None, bio: str | None = None, state: str = 'published') -> Profile:
        profile = Profile(name=name, headline=headline, summary=summary, location=location, availability=availability, bio=bio, state=state)
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def create_project(self, *, title: str, slug: str, summary: str, state: str = 'published', featured: bool = False, sort_order: int = 0, **kwargs) -> Project:
        project = Project(title=title, slug=slug, summary=summary, state=state, featured=featured, sort_order=sort_order, **kwargs)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
