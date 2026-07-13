import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from database import Base, get_db
from main import app
from models import Task, UserStory


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with patch("main.init_db"):
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()


def sample_user_story() -> UserStory:
    return UserStory(
        project="Task Manager",
        role="desarrollador",
        goal="crear historias de usuario",
        reason="organizar el backlog",
        description="Historia generada para pruebas automatizadas.",
        priority="alta",
        story_points=5,
        effort_hours=12.5,
    )


def sample_task(user_story_id: int) -> Task:
    return Task(
        title="Definir modelo de datos",
        description="Crear tablas UserStory y Task en MySQL.",
        priority="media",
        effort_hours=4.0,
        status="pendiente",
        assigned_to="Pablo",
        user_story_id=user_story_id,
    )
