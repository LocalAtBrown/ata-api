from typing import Generator

from ata_db_models.helpers import get_conn_string
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import create_engine

engine = create_engine(url=get_conn_string())
session_factory = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def create_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that opens and closes a DB session.
    (See: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/.)
    """
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
