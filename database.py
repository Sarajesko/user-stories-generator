from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_database_url

engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> str:
    with engine.connect() as connection:
        return connection.execute(text("SELECT DATABASE()")).scalar_one()


def init_db() -> None:
    from models import Task, UserStory  # noqa: F401

    Base.metadata.create_all(bind=engine)
