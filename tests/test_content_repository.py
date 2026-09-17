from os import environ

environ["DATABASE_URL"] = "sqlite:///./isolated_repository_test.db"

from app.db import get_session_local
from app.repositories.content import ContentRepository
from app.main import create_app


def test_only_published_projects_are_visible():
    create_app()
    session = get_session_local()()
    repo = ContentRepository(session)
    repo.create_project(title="Workflow Automation Platform", slug="workflow-automation-platform", summary="existing", state="published")
    repo.create_project(title="Draft", slug="draft", summary="draft", state="draft")
    repo.create_project(title="Live", slug="live", summary="live", state="published")
    projects = repo.list_projects()
    assert {project.title for project in projects} == {"Live", "Workflow Automation Platform"}
    session.close()
