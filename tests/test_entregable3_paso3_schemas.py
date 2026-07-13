"""Entregable 3 - Paso 3: schemas Pydantic para salidas estructuradas del LLM."""

import pytest
from pydantic import ValidationError

from schemas import TaskSchema, TasksSchema, UserStoriesSchema, UserStorySchema
from tests.conftest import sample_task, sample_user_story

pytestmark = pytest.mark.entregable3_paso3


def test_user_story_schema_valid_data() -> None:
    schema = UserStorySchema(
        project="Task Manager",
        role="product owner",
        goal="priorizar el backlog",
        reason="mejorar la planificacion",
        description="Historia valida para pruebas.",
        priority="media",
        story_points=3,
        effort_hours=8.0,
    )
    assert schema.priority == "media"
    assert schema.story_points == 3


@pytest.mark.parametrize("story_points", [0, 9, -1])
def test_user_story_schema_rejects_invalid_story_points(story_points: int) -> None:
    with pytest.raises(ValidationError):
        UserStorySchema(
            project="Task Manager",
            role="dev",
            goal="objetivo",
            reason="razon",
            description="descripcion",
            priority="baja",
            story_points=story_points,
            effort_hours=2.0,
        )


@pytest.mark.parametrize("priority", ["urgente", "critica", ""])
def test_user_story_schema_rejects_invalid_priority(priority: str) -> None:
    with pytest.raises(ValidationError):
        UserStorySchema(
            project="Task Manager",
            role="dev",
            goal="objetivo",
            reason="razon",
            description="descripcion",
            priority=priority,
            story_points=2,
            effort_hours=2.0,
        )


def test_user_stories_schema_wraps_list() -> None:
    payload = UserStoriesSchema(
        user_stories=[
            UserStorySchema(
                project="A",
                role="r1",
                goal="g1",
                reason="z1",
                description="d1",
                priority="alta",
                story_points=5,
                effort_hours=10.0,
            )
        ]
    )
    assert len(payload.user_stories) == 1


def test_task_schema_valid_data() -> None:
    schema = TaskSchema(
        title="Implementar login",
        description="Crear endpoint de autenticacion.",
        priority="alta",
        effort_hours=6.5,
        status="pendiente",
        assigned_to="Pablo",
    )
    assert schema.status == "pendiente"


@pytest.mark.parametrize("status", ["hecha", "todo", ""])
def test_task_schema_rejects_invalid_status(status: str) -> None:
    with pytest.raises(ValidationError):
        TaskSchema(
            title="Tarea",
            description="Descripcion",
            priority="media",
            effort_hours=1.0,
            status=status,
            assigned_to="Ana",
        )


def test_tasks_schema_wraps_list() -> None:
    payload = TasksSchema(
        tasks=[
            TaskSchema(
                title="T1",
                description="D1",
                priority="baja",
                effort_hours=1.0,
                status="completada",
                assigned_to="Luis",
            )
        ]
    )
    assert len(payload.tasks) == 1


def test_user_story_schema_from_orm(db_session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    schema = UserStorySchema.model_validate(story)
    assert schema.project == "Task Manager"
    assert schema.story_points == 5


def test_task_schema_from_orm(db_session) -> None:
    story = sample_user_story()
    db_session.add(story)
    db_session.commit()

    task = sample_task(story.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    schema = TaskSchema.model_validate(task)
    assert schema.title == "Definir modelo de datos"
    assert schema.assigned_to == "Pablo"
