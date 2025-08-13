from datetime import datetime, timedelta, timezone
import os
import secrets
import string
from typing import Annotated, Any

import aiofiles
from fastapi import Depends, FastAPI, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import flowio
import jwt
from sqlmodel import Session, SQLModel, create_engine, select
from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext

from app.models import ShortLinkPublic, TokenPayload, User, ShortLink, Token
import uuid

from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError


class Settings(BaseSettings):
    postgres_url: str = ''
    API_URL: str = 'http://127.0.0.1:8000'
    SECRET_KEY: str = secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

engine = create_engine(settings.postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_URL}/login",
    auto_error=False,
)

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, token: TokenDep, required: bool = True) -> User | None:
    if not token:
        if required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )

    user = session.get(User, token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(lambda session=Depends(get_session), token=Depends(reusable_oauth2): get_current_user(session, token, required=False))]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@app.post("/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(
        session=session, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return Token(
        access_token=create_access_token(
            user.id, expires_delta=timedelta(minutes=60)
        )
    )

@app.get("/short-link/{slug}")
def get_short_link_content(slug: str, session: SessionDep):
    short_link = session.exec(select(ShortLink).where(ShortLink.slug == slug)).first()
    if not short_link:
        raise HTTPException(status_code=404, detail="Short link not found")

    storage_full_filename = os.path.join('storage', short_link.filename)
    def iterfile():
        with open(storage_full_filename, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="application/vnd.isac.fcs")


def generate_unique_slug(session: SessionDep) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        slug = ''.join(secrets.choice(chars) for _ in range(8))
        existing = session.exec(select(ShortLink).where(ShortLink.slug == slug)).first()
        if not existing:
            return slug


@app.post("/short-link/", response_model=ShortLinkPublic)
async def short_link_create(file: UploadFile, session: SessionDep, current_user: OptionalCurrentUser):
    filesize = file.size if file.size else 0
    if filesize == 0:
        raise HTTPException(status_code=400, detail="File size cannot be zero")
    if filesize > 1000 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 1000MB limit")
    
    storage_filename = str(uuid.uuid4()) + '.fcs'
    storage_full_filename = os.path.join('storage', storage_filename)
    async with aiofiles.open(storage_full_filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    try:
        fd = flowio.FlowData(storage_full_filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid FCS file")

    short_link = ShortLink(
        slug=generate_unique_slug(session),
        original_file=file.filename if file.filename else "",
        filename = storage_filename,
        filesize=filesize,
        created_at=datetime.now(timezone.utc),
        fcs_version=fd.version
    )

    session.add(short_link)
    session.commit()
    session.refresh(short_link)

    # print(current_user.email if current_user else "Anonymous user")

    return short_link


# @app.get("/heroes/")
# def read_heroes(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[Hero]:
#     heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
#     return heroes


# @app.get("/heroes/{hero_id}")
# def read_hero(hero_id: int, session: SessionDep) -> Hero:
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     return hero


# @app.delete("/heroes/{hero_id}")
# def delete_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}
