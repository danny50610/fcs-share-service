
from fastapi.testclient import TestClient
import pytest

from sqlmodel import SQLModel, Session, create_engine

from app.main import app, get_session, settings


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(settings.postgres_test_url)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
