from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str = Field()


class ShortLinkBase(SQLModel):
    original_file: str = Field()


class ShortLink(ShortLinkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    filename: str = Field()
    filesize: int = Field()
    created_at: datetime | None = Field()
    fcs_version: str = Field()


class ShortLinkPublic(ShortLinkBase):
    slug: str
    original_file: str
    filesize: int
    created_at: datetime | None
    fcs_version: str


# class ShortLinkUpdate(ShortLinkBase):
#     pass


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
