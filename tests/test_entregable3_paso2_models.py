"""Entregable 3 - Paso 2: modelos SQLAlchemy, relaciones y persistencia."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from models import Task, UserStory
from tests.conftest import sample_task, sample_user_story

pytestmark = pytest.mark.entregable3_paso2


def test_tables_are_registered() -> None:
    table_names = {"user_stories", "tasks"}
    assert table_names.issubset(UserStory.metadata.tables.keys() | Task.metadata.tables.keys())


def test_init_db_creates_expected_columns(db_session: Session) -> None:
    inspector = inspect(db_session.bind)
    user_story_columns = {column["name"] for column in inspector.get_columns("user_stories")}
    task_columns = {column["name"] for column in inspector.get_columns("tasks")}

    assert user_story_columns == {
        "id",
        "project",
        "role",
        "goal",
        "reason",
        "description",
        "priority",
        "story_points",
        "effort_hours",
        "created_at",
    }
    assert task_columns == {
        "id",
        "title",
        "description",
        "priority",
        "effort_hours",
        "status",
        "assigned_to",
        "user_story_id",
        "created_at",
    }


def test_user_story_persists(db_session: Session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    assert story.id is not None
    assert story.project == "Task Manager"
    assert story.story_points == 5
    assert story.created_at is not None


def test_task_is_linked_to_user_story(db_session: Session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()

    task = sample_task(story.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    assert task.user_story_id == story.id
    assert task.user_story.project == "Task Manager"
    assert task.assigned_to == "Pablo"


def test_user_story_has_many_tasks(db_session: Session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()

    db_session.add_all(
        [
            sample_task(story.id),
            Task(
                title="Crear endpoints",
                description="Implementar rutas FastAPI para historias y tareas.",
                priority="alta",
                effort_hours=6.0,
                status="en progreso",
                assigned_to="Ana",
                user_story_id=story.id,
            ),
        ]
    )
    db_session.commit()
    db_session.refresh(story)

    assert len(story.tasks) == 2
    assert {task.title for task in story.tasks} == {
        "Definir modelo de datos",
        "Crear endpoints",
    }


def test_delete_user_story_cascades_tasks(db_session: Session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()

    db_session.add(sample_task(story.id))
    db_session.commit()

    db_session.delete(story)
    db_session.commit()

    assert db_session.query(Task).count() == 0
    assert db_session.query(UserStory).count() == 0
