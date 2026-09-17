from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

project_skill = Table(
    'project_skill',
    Base.metadata,
    Column('project_id', ForeignKey('project.id'), primary_key=True),
    Column('skill_id', ForeignKey('skill.id'), primary_key=True),
)


class Profile(Base):
    __tablename__ = 'profile'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str] = mapped_column(String(20), default='published')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    links: Mapped[list['Link']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    experiences: Mapped[list['Experience']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    education: Mapped[list['Education']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    certifications: Mapped[list['Certification']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    media: Mapped[list['MediaAsset']] = relationship(back_populates='profile', cascade='all, delete-orphan')


class Link(Base):
    __tablename__ = 'link'
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey('profile.id'), nullable=True)
    profile: Mapped[Profile | None] = relationship(back_populates='links')


class Experience(Base):
    __tablename__ = 'experience'
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    company: Mapped[str] = mapped_column(String(120), nullable=False)
    employment_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    state: Mapped[str] = mapped_column(String(20), default='published')
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey('profile.id'), nullable=True)
    profile: Mapped[Profile | None] = relationship(back_populates='experiences')


class Education(Base):
    __tablename__ = 'education'
    id: Mapped[int] = mapped_column(primary_key=True)
    school: Mapped[str] = mapped_column(String(150), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    honors: Mapped[str | None] = mapped_column(String(200), nullable=True)
    state: Mapped[str] = mapped_column(String(20), default='published')
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey('profile.id'), nullable=True)
    profile: Mapped[Profile | None] = relationship(back_populates='education')


class Skill(Base):
    __tablename__ = 'skill'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default='general')
    proficiency: Mapped[str | None] = mapped_column(String(80), nullable=True)
    state: Mapped[str] = mapped_column(String(20), default='published')
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    projects: Mapped[list['Project']] = relationship(secondary=project_skill, back_populates='skills')


class Project(Base):
    __tablename__ = 'project'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(String(600), nullable=False)
    problem: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    technology: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    repo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    impact: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    state: Mapped[str] = mapped_column(String(20), default='published')
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    skills: Mapped[list[Skill]] = relationship(secondary=project_skill, back_populates='projects')


class Certification(Base):
    __tablename__ = 'certification'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    issued_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str] = mapped_column(String(20), default='published')
    profile_id: Mapped[int | None] = mapped_column(ForeignKey('profile.id'), nullable=True)
    profile: Mapped[Profile | None] = relationship(back_populates='certifications')


class MediaAsset(Base):
    __tablename__ = 'media_asset'
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    media_type: Mapped[str] = mapped_column(String(40), default='image')
    profile_id: Mapped[int | None] = mapped_column(ForeignKey('profile.id'), nullable=True)
    profile: Mapped[Profile | None] = relationship(back_populates='media')
