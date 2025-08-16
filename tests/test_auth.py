
import bcrypt
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User

from tests.fixture import session_fixture, client_fixture

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
