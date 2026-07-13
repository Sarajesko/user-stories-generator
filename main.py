from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import check_database_connection, init_db
from routers.user_stories import router as user_stories_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="User Stories Generator",
    description="Generador de historias de usuario y tareas con IA.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(user_stories_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "User Stories Generator running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    database_name = check_database_connection()
    return {"status": "ok", "database": database_name or "connected"}
