"""Entregable 3 - Paso 4: servicio LangChain con salida estructurada (mocks en pytest)."""

from unittest.mock import MagicMock, patch

import pytest

from models.user_story import UserStory
from schemas.task import TaskSchema, TasksSchema
from schemas.user_story import UserStorySchema
from services import llm_service as llm_module
from services.llm_service import LLMServiceError, generar_historia, generar_tareas

pytestmark = pytest.mark.entregable3_paso4


@pytest.fixture
def sample_story_model() -> UserStory:
    return UserStory(
        id=1,
        project="Task Manager",
        role="product owner",
        goal="priorizar el backlog",
        reason="mejorar la planificacion",
        description="Como PO quiero generar historias para organizar el desarrollo.",
        priority="alta",
        story_points=5,
        effort_hours=16.0,
    )


@pytest.fixture
def mock_user_story_schema() -> UserStorySchema:
    return UserStorySchema(
        project="Task Manager",
        role="desarrollador",
        goal="crear API REST",
        reason="gestionar tareas del equipo",
        description="Historia generada para exponer un CRUD de tareas.",
        priority="media",
        story_points=3,
        effort_hours=10.0,
    )


@pytest.fixture
def mock_task_schemas() -> list[TaskSchema]:
    return [
        TaskSchema(
            title="Definir modelos",
            description="Crear modelos SQLAlchemy para UserStory y Task.",
            priority="alta",
            effort_hours=4.0,
            status="pendiente",
            assigned_to="Pablo",
        ),
        TaskSchema(
            title="Crear endpoints",
            description="Implementar rutas FastAPI para historias y tareas.",
            priority="media",
            effort_hours=6.0,
            status="pendiente",
            assigned_to="Ana",
        ),
    ]


def test_generar_historia_returns_user_story_schema(
    mock_user_story_schema: UserStorySchema,
) -> None:
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = mock_user_story_schema
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured

    result = generar_historia("App de gestion de tareas para un equipo Scrum", llm=mock_llm)

    assert result.project == "Task Manager"
    assert result.story_points == 3
    mock_llm.with_structured_output.assert_called_once_with(UserStorySchema)
    mock_structured.invoke.assert_called_once()


def test_generar_tareas_returns_task_list(
    sample_story_model: UserStory,
    mock_task_schemas: list[TaskSchema],
) -> None:
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TasksSchema(tasks=mock_task_schemas)
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured

    result = generar_tareas(sample_story_model, llm=mock_llm)

    assert len(result) == 2
    assert result[0].title == "Definir modelos"
    mock_llm.with_structured_output.assert_called_once_with(TasksSchema)
    human_message = mock_structured.invoke.call_args[0][0][1].content
    assert "Descripcion:" in human_message
    assert str(sample_story_model.effort_hours) in human_message


def test_generar_tareas_raises_when_empty_list(sample_story_model: UserStory) -> None:
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TasksSchema(tasks=[])
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured

    with pytest.raises(LLMServiceError, match="no devolvio ninguna tarea"):
        generar_tareas(sample_story_model, llm=mock_llm)


@patch.object(llm_module, "load_azure_settings")
def test_get_llm_raises_when_config_missing(mock_load_settings: MagicMock) -> None:
    from config import ConfigurationError
    from services.llm_service import get_llm

    mock_load_settings.side_effect = ConfigurationError("Missing required environment variable: AZURE_OPENAI_API_KEY")

    with pytest.raises(LLMServiceError, match="AZURE_OPENAI_API_KEY"):
        get_llm()
