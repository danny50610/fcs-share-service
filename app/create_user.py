
import secrets
import string
import sys
import bcrypt
from sqlmodel import Session, create_engine

from app.models import User
from app.settings import settings


def main():
    email = sys.argv[1]
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

    engine = create_engine(settings.postgres_url)
    with Session(engine) as session:
        user = User(
            email=email,
            password=bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf-8'),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    print(f"User created with email: {email} and password: {password}")


if __name__ == "__main__":
    main()
