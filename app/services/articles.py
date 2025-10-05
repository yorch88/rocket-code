# app/services/articles.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..schemas.schemas import ArticleCreate, ArticleUpdate, ArticleOut
from ..repositories import articles as repo
from ..repositories.articles import ListFilters  # <- importa el dataclass
from ..cache import get_cached_article, set_cached_article, invalidate_article


def create_article(db: Session, payload: ArticleCreate):
    try:
        article = repo.create_article(db, payload)
        # Si quieres cachear al crear:
        set_cached_article(article.id, article)
        return article
    except Exception as e:  # convertimos a HTTPException y preservamos cadena
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


def get_article(db: Session, article_id: int):
    cached = get_cached_article(article_id)
    if cached is not None:
        # Devolver como modelo (o dict). Ambas funcionan con response_model.
        return ArticleOut(**cached)

    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    set_cached_article(article_id, article)
    return article


def update_article(db: Session, article_id: int, payload: ArticleUpdate):
    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    updated = repo.update_article(db, article, payload)

    # Actualiza cache con la versión serializada
    invalidate_article(article_id)
    set_cached_article(article_id, updated)
    return updated


def delete_article(db: Session, article_id: int):
    article = repo.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    repo.delete_article(db, article)
    invalidate_article(article_id)


def list_articles(db: Session, **kw):
    filters = ListFilters(**kw)
    return repo.list_articles(db, filters)


def search_articles(db: Session, q: str, limit: int = 20):
    return repo.search_articles(db, q, limit)
