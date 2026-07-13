"""Entregable 3 - Paso 5: endpoints y vistas Jinja (IA mockeada)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Task, UserStory
from schemas.task import TaskSchema
from schemas.user_story import UserStorySchema
from tests.conftest import sample_task, sample_user_story

pytestmark = pytest.mark.entregable3_paso5


@pytest.fixture
def mock_story_schema() -> UserStorySchema:
    return UserStorySchema(
        project="Task Manager",
        role="desarrollador",
        goal="crear historias de usuario",
        reason="organizar el backlog",
        description="Historia generada desde endpoint de prueba.",
        priority="alta",
        story_points=5,
        effort_hours=12.5,
    )


@pytest.fixture
def mock_task_schemas() -> list[TaskSchema]:
    return [
        TaskSchema(
            title="Definir modelos",
            description="Crear tablas UserStory y Task.",
            priority="media",
            effort_hours=4.0,
            status="pendiente",
            assigned_to="Pablo",
        )
    ]


def test_get_user_stories_renders_form_and_list(
    client: TestClient,
    db_session: Session,
) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()

    response = client.get("/user-stories")

    assert response.status_code == 200
    assert "Generar historia con IA" in response.text
    assert "Task Manager" in response.text
    assert "Generar tareas" in response.text


@patch("routers.user_stories.llm_service.generar_historia")
def test_post_user_stories_creates_story_and_redirects(
    mock_generar_historia,
    client: TestClient,
    db_session: Session,
    mock_story_schema: UserStorySchema,
) -> None:
    mock_generar_historia.return_value = mock_story_schema

    response = client.post(
        "/user-stories",
        data={"prompt": "App de tareas para equipos agile"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/user-stories"
    assert db_session.query(UserStory).count() == 1
    mock_generar_historia.assert_called_once_with("App de tareas para equipos agile")


@patch("routers.user_stories.llm_service.generar_tareas")
def test_post_generate_tasks_creates_tasks_and_redirects(
    mock_generar_tareas,
    client: TestClient,
    db_session: Session,
    mock_task_schemas: list[TaskSchema],
) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)
    mock_generar_tareas.return_value = mock_task_schemas

    response = client.post(
        f"/user-stories/{story.id}/generate-tasks",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/user-stories/{story.id}/tasks"
    assert db_session.query(Task).count() == 1
    mock_generar_tareas.assert_called_once()


def test_get_tasks_page_renders_story_and_tasks(
    client: TestClient,
    db_session: Session,
) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    task = sample_task(story.id)
    db_session.add(task)
    db_session.commit()

    response = client.get(f"/user-stories/{story.id}/tasks")

    assert response.status_code == 200
    assert "Definir modelo de datos" in response.text
    assert "Pablo" in response.text
    assert "Generar tareas" in response.text


def test_get_tasks_returns_404_for_missing_story(client: TestClient) -> None:
    response = client.get("/user-stories/999/tasks")
    assert response.status_code == 404


def test_post_generate_tasks_returns_404_for_missing_story(client: TestClient) -> None:
    response = client.post("/user-stories/999/generate-tasks")
    assert response.status_code == 404
