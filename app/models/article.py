from sqlalchemy import String, Integer, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.db import Base

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(255), default="")
    author: Mapped[str] = mapped_column(String(120), index=True)
    published_at: Mapped[DateTime | None] = mapped_column(DateTime,
                                                          nullable=True,
                                                          index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 server_default=func.now() # pylint: disable=not-callable
                                                 )
    updated_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 server_default=func.now(), # pylint: disable=not-callable
                                                 onupdate=func.now() # pylint: disable=not-callable
                                                 )

    __table_args__ = (
        UniqueConstraint("title", "author", name="uq_title_author"),
    )
