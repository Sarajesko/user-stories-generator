from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

from config import AzureOpenAISettings, ConfigurationError, load_azure_settings
from models.user_story import UserStory
from schemas.task import TaskSchema, TasksSchema
from schemas.user_story import UserStorySchema


class LLMServiceError(Exception):
    pass


def _reload_env() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)


def get_llm(settings: AzureOpenAISettings | None = None) -> BaseChatModel:
    try:
        if settings is None:
            _reload_env()
        cfg = settings or load_azure_settings()
    except ConfigurationError as error:
        raise LLMServiceError(str(error)) from error

    return AzureChatOpenAI(
        azure_endpoint=cfg.endpoint,
        api_key=cfg.api_key,
        api_version=cfg.api_version,
        azure_deployment=cfg.deployment,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        top_p=cfg.top_p,
    )


def generar_historia(prompt: str, llm: BaseChatModel | None = None) -> UserStorySchema:
    model = llm or get_llm()
    structured = model.with_structured_output(UserStorySchema)

    system_prompt = (
        "Eres un experto en analisis de requisitos y metodologias agiles. "
        "A partir del contexto del usuario, genera una historia de usuario completa "
        "en espanol con formato 'Como [rol], quiero [objetivo], para [razon]'. "
        "Rellena project, role, goal, reason y una description detallada y accionable. "
        "Asigna priority entre: baja, media, alta o bloqueante. "
        "Estima story_points como entero entre 1 y 8 segun complejidad relativa. "
        "Estima effort_hours como numero positivo de horas de trabajo del equipo."
    )

    try:
        result = structured.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ]
        )
    except Exception as error:
        raise LLMServiceError(f"Error al generar la historia de usuario: {error}") from error

    if not isinstance(result, UserStorySchema):
        raise LLMServiceError("La respuesta del modelo no es un UserStorySchema valido")
    return result


def generar_tareas(historia: UserStory, llm: BaseChatModel | None = None) -> list[TaskSchema]:
    model = llm or get_llm()
    structured = model.with_structured_output(TasksSchema)

    system_prompt = (
        "Eres un tech lead que descompone historias de usuario en tareas tecnicas ejecutables. "
        "Genera entre 3 y 6 tareas en espanol, cada una con titulo corto, descripcion clara, "
        "priority (baja, media, alta o bloqueante), effort_hours positivo, "
        "status inicial 'pendiente' y assigned_to con un nombre de persona del equipo. "
        "La suma de effort_hours de las tareas debe ser coherente con el esfuerzo de la historia."
    )

    human_prompt = (
        f"Proyecto: {historia.project}\n"
        f"Rol: {historia.role}\n"
        f"Objetivo: {historia.goal}\n"
        f"Razon: {historia.reason}\n"
        f"Descripcion: {historia.description}\n"
        f"Prioridad de la historia: {historia.priority}\n"
        f"Horas estimadas de la historia: {historia.effort_hours}\n"
        "Descompone esta historia en tareas concretas para el equipo de desarrollo."
    )

    try:
        result = structured.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
    except Exception as error:
        raise LLMServiceError(f"Error al generar las tareas: {error}") from error

    if not isinstance(result, TasksSchema):
        raise LLMServiceError("La respuesta del modelo no es un TasksSchema valido")
    if not result.tasks:
        raise LLMServiceError("El modelo no devolvio ninguna tarea")
    return result.tasks
