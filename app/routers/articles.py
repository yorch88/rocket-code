from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from sqlalchemy.orm import Session

from ..db.db import get_db
from ..schemas.schemas import ArticleCreate, ArticleUpdate, ArticleOut
from ..services import articles as svc
from ..dependencies import require_api_key
from ..rate_limit import rate_limiter


router = APIRouter(
    prefix="/articles",
    tags=["articles"],
    dependencies=[Depends(require_api_key), Depends(rate_limiter)],
)


# ---- Query params model (avoids R0913/R0917) ----
class ListQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    author: Optional[str] = None
    tag: Optional[str] = None
    order: Literal["asc", "desc"] = "desc"


@router.post(
    "",
    response_model=ArticleOut,
    status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db)):
    return await run_in_threadpool(svc.create_article, db, payload)


@router.put(
    "/{article_id}",
    response_model=ArticleOut)
async def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db)):
    return await run_in_threadpool(
        svc.update_article,
        db,
        article_id,
        payload,
    )


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)):
    await run_in_threadpool(svc.delete_article, db, article_id)
    return


@router.get(
    "",
    response_model=list[ArticleOut])
async def list_articles(
    params: ListQuery = Depends(),
    db: Session = Depends(get_db)):
    """Return a paginated list of articles."""
    filters = params.dict()
    items, _ = await run_in_threadpool(svc.list_articles, db, **filters)
    return items


@router.get(
    "/search",
    summary="Search articles")
async def search_articles(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)):
    return await run_in_threadpool(
        svc.search_articles,
        db,
        q=q,
        limit=limit,
    )


@router.get(
    "/{article_id}",
    summary="Get article by ID")
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)):
    return await run_in_threadpool(
        svc.get_article,
        db,
        article_id=article_id,
    )
