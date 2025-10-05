from typing import Optional, Tuple, List
from dataclasses import dataclass

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from ..models.article import Article
from ..schemas.schemas import ArticleCreate, ArticleUpdate


def create_article(db: Session, payload: ArticleCreate) -> Article:
    """
    Create and persist a new Article record in the database.

    Args:
        db (Session): Active SQLAlchemy database session.
        payload (ArticleCreate): Pydantic model containing validated data.

    Returns:
        Article: The newly created ORM Article instance.
    """
    article = Article(**payload.dict())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """
    Retrieve an Article by its ID.

    Args:
        db (Session): Active SQLAlchemy session.
        article_id (int): Unique identifier of the Article.

    Returns:
        Optional[Article]: The found Article or None if not found.
    """
    return db.get(Article, article_id)


def update_article(db: Session, article: Article, payload: ArticleUpdate) -> Article:
    """
    Apply partial updates to an existing Article record.

    Args:
        db (Session): Active SQLAlchemy session.
        article (Article): The target ORM instance.
        payload (ArticleUpdate): Fields to be updated.

    Returns:
        Article: The updated ORM Article instance.
    """
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(article, field, value)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """
    Permanently delete an Article record from the database.

    Args:
        db (Session): Active SQLAlchemy session.
        article (Article): The ORM instance to be deleted.
    """
    db.delete(article)
    db.commit()


@dataclass(slots=True)
class ListFilters:
    """
    Strongly typed data container for article listing filters.
    """
    page: int = 1
    page_size: int = 10
    author: Optional[str] = None
    tag: Optional[str] = None
    order: str = "desc"  # Accepts "asc" or "desc"


def list_articles(db: Session, filters: Optional[ListFilters] = None) -> Tuple[List[Article], int]:
    """
    Retrieve a paginated list of articles with optional filtering and sorting.

    Args:
        db (Session): Active SQLAlchemy session.
        filters (Optional[ListFilters]): Filtering and pagination parameters.

    Returns:
        Tuple[List[Article], int]: (Paginated list of ORM Articles, total count)
    """
    if filters is None:
        filters = ListFilters()

    stmt = select(Article)
    count_stmt = select(func.count()).select_from(Article)  # pylint: disable=not-callable

    if filters.author:
        stmt = stmt.where(Article.author == filters.author)
        count_stmt = count_stmt.where(Article.author == filters.author)

    if filters.tag:
        stmt = stmt.where(Article.tags.ilike(f"%{filters.tag}%"))
        count_stmt = count_stmt.where(Article.tags.ilike(f"%{filters.tag}%"))

    # Sort by publication date, default to descending order
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
    """
    Perform a simple text search on article title or body.

    Args:
        db (Session): Active SQLAlchemy session.
        q (str): Search query string.
        limit (int): Maximum number of results to return.

    Returns:
        List[Article]: Matching Article ORM objects.
    """
    stmt = (
        select(Article)
        .where(or_(Article.title.ilike(f"%{q}%"), Article.body.ilike(f"%{q}%")))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
