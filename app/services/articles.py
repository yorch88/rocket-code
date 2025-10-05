from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..schemas.schemas import ArticleCreate, ArticleUpdate, ArticleOut
from ..repositories import articles as repo
from ..repositories.articles import ListFilters
from ..cache import get_cached_article, set_cached_article, invalidate_article
from ..models.article import Article


def _serialize_for_cache(article: Article) -> Dict[str, Any]:
    """
    Convert an ORM Article instance into a serializable dict for caching.
    """
    return ArticleOut.from_orm(article).dict()


def _hydrate_from_cache(data: Dict[str, Any]) -> ArticleOut:
    """
    Convert a cached dict back into an ArticleOut Pydantic object.
    """
    return ArticleOut(**data)


def create_article(db: Session, payload: ArticleCreate) -> Article:
    """
    Create a new Article and store it in the cache.

    Returns:
        Article: The newly created ORM instance.
    Raises:
        HTTPException: If any database or validation error occurs.
    """
    try:
        article = repo.create_article(db, payload)
        if getattr(article, "id", None):
            set_cached_article(article.id, _serialize_for_cache(article))
        return article
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


def get_article(db: Session, article_id: int) -> Article | ArticleOut:
    """
    Retrieve an article by ID, checking cache first.

    Returns:
        Article | ArticleOut: The article ORM or cached model.
    Raises:
        HTTPException: If not found.
    """
    cached = get_cached_article(article_id)
    if cached is not None:
        return _hydrate_from_cache(cached)

    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    set_cached_article(article_id, _serialize_for_cache(article))
    return article


def update_article(db: Session, article_id: int, payload: ArticleUpdate) -> Article:
    """
    Update an existing article and refresh its cache.

    Returns:
        Article: Updated ORM instance.
    Raises:
        HTTPException: If the article does not exist.
    """
    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    updated = repo.update_article(db, article, payload)
    invalidate_article(article_id)
    set_cached_article(article_id, _serialize_for_cache(updated))
    return updated


def delete_article(db: Session, article_id: int) -> None:
    """
    Delete an article by ID and invalidate its cache.

    Raises:
        HTTPException: If the article does not exist.
    """
    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    repo.delete_article(db, article)
    invalidate_article(article_id)


def list_articles(db: Session, **kwargs) -> Tuple[List[Article], int]:
    """
    Retrieve a paginated list of articles through the repository layer.

    Returns:
        Tuple[List[Article], int]: List of ORM Articles and total count.
    """
    filters = ListFilters(**kwargs)
    return repo.list_articles(db, filters)


def search_articles(db: Session, q: str, limit: int = 20) -> List[Article]:
    """
    Perform a full-text search across article titles and bodies.

    Returns:
        List[Article]: Matching ORM instances.
    """
    return repo.search_articles(db, q, limit)
