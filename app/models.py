from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str = Field()


class ShortLink(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    original_file: str
    filesize: int = Field()
    created_at: datetime | None = Field()
    fcs_version: str = Field()

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
