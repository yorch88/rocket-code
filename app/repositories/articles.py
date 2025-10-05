# app/repositories/articles.py

from typing import Optional, Tuple, List
from dataclasses import dataclass

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from ..models.article import Article
from ..schemas.schemas import ArticleCreate, ArticleUpdate


def create_article(db: Session, payload: ArticleCreate) -> Article:
    a = Article(**payload.dict())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def get_article(db: Session, article_id: int) -> Optional[Article]:
    return db.get(Article, article_id)


def update_article(db: Session, article: Article, payload: ArticleUpdate) -> Article:
    for f, v in payload.dict(exclude_unset=True).items():
        setattr(article, f, v)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    db.delete(article)
    db.commit()


@dataclass(slots=True)
class ListFilters:
    page: int = 1
    page_size: int = 10
    author: Optional[str] = None
    tag: Optional[str] = None
    order: str = "desc"  # "asc" | "desc"


def list_articles(db: Session, filters: Optional[ListFilters] = None) -> Tuple[List[Article], int]:
    """
    Returns (items, total_count)
    """
    if filters is None:
        filters = ListFilters()

    stmt = select(Article)
    count_stmt = select(func.count() # pylint: disable=not-callable
                        ).select_from(Article)

    if filters.author:
        stmt = stmt.where(Article.author == filters.author)
        count_stmt = count_stmt.where(Article.author == filters.author)

    if filters.tag:
        stmt = stmt.where(Article.tags.ilike(f"%{filters.tag}%"))
        count_stmt = count_stmt.where(Article.tags.ilike(f"%{filters.tag}%"))

    # Order by published_at (nulls last), default desc
    if filters.order == "asc":
        stmt = stmt.order_by(Article.published_at.asc().nullslast())
    else:
        stmt = stmt.order_by(Article.published_at.desc().nullslast())

    # Pagination
    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)

    items = list(db.execute(stmt).scalars().all())
    total = db.execute(count_stmt).scalar_one()

    return items, total


def search_articles(db: Session, q: str, limit: int = 20) -> List[Article]:
    stmt = (
        select(Article)
        .where(or_(Article.title.ilike(f"%{q}%"), Article.body.ilike(f"%{q}%")))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
