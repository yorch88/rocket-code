from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module


def normalize_tags(value: str | List[str] | None) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ";".join([t.strip() for t in value if t.strip()])
    return value


class ArticleBase(BaseModel):
    title: str = Field(..., max_length=255)
    body: str
    tags: Optional[str | list[str]] = ""
    author: str = Field(..., max_length=120)
    published_at: Optional[datetime] = None

    @validator("tags", pre=True)  # pylint: disable=no-self-argument
    @classmethod
    def join_tags(cls, v):
        return normalize_tags(v)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[str | list[str]] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None

    @validator("tags", pre=True)  # pylint: disable=no-self-argument
    @classmethod
    def join_tags(cls, v):
        return normalize_tags(v)


class ArticleOut(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: str

    class Config:
        orm_mode = True
