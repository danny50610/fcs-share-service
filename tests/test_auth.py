
import bcrypt
from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.main import get_session, settings
from app.main import app
from app.models import User

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


def test_login(session: Session, client: TestClient):
    user = User(
        email='test@example.com',
        password=bcrypt.hashpw(b'testpassword', bcrypt.gensalt()).decode('utf-8'),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    print(response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
