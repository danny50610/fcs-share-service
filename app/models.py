from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str
    password: str = Field()
    short_links: List["ShortLink"] = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: int


class ShortLinkBase(SQLModel):
    original_file: str = Field()


class ShortLink(ShortLinkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    filename: str = Field()
    filesize: int = Field()
    fcs_version: str = Field()
    visibility: str = Field(default="private")  # 'public' or 'private'
    user_id: int | None = Field(default=None, foreign_key="user.id")
    created_at: datetime | None = Field()

    user: Optional[User] = Relationship(back_populates="short_links")


class ShortLinkPublic(ShortLinkBase):
    slug: str
    original_file: str
    filesize: int
    created_at: datetime | None
    fcs_version: str



# ------------------------------
# Token Models
# ------------------------------

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[str] = None
