from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.task import Task
from models.user_story import UserStory
from services import llm_service
from services.llm_service import LLMServiceError
from templating import templates

router = APIRouter(tags=["user-stories"])


@router.get("/user-stories")
def list_user_stories(request: Request, db: Session = Depends(get_db)):
    stories = db.scalars(
        select(UserStory).order_by(UserStory.created_at.desc())
    ).all()
    return templates.TemplateResponse(
        request,
        "user-stories.html",
        {"stories": stories},
    )


@router.post("/user-stories")
def create_user_story(
    prompt: str = Form(...),
    db: Session = Depends(get_db),
):
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacio")

    try:
        story_schema = llm_service.generar_historia(prompt.strip())
    except LLMServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    story = UserStory(**story_schema.model_dump())
    db.add(story)
    db.commit()
    return RedirectResponse(url="/user-stories", status_code=303)


@router.post("/user-stories/{story_id}/generate-tasks")
def generate_tasks(story_id: int, db: Session = Depends(get_db)):
    story = db.get(UserStory, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Historia no encontrada")

    try:
        task_schemas = llm_service.generar_tareas(story)
    except LLMServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    for task_schema in task_schemas:
        db.add(Task(user_story_id=story.id, **task_schema.model_dump()))
    db.commit()
    return RedirectResponse(url=f"/user-stories/{story_id}/tasks", status_code=303)


@router.get("/user-stories/{story_id}/tasks")
def list_tasks(story_id: int, request: Request, db: Session = Depends(get_db)):
    story = db.get(UserStory, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Historia no encontrada")

    return templates.TemplateResponse(
        request,
        "tasks.html",
        {"story": story, "tasks": story.tasks},
    )
