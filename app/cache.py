from typing import Any, Optional
import json
import redis
from .config import get_settings
from .schemas.schemas import ArticleOut

_settings = get_settings()
_r = redis.Redis(host=_settings.REDIS_HOST, port=_settings.REDIS_PORT, db=_settings.REDIS_DB)
_TTL = getattr(_settings, "CACHE_TTL_SECONDS", 90)


def cache_key(article_id: int) -> str:
    return f"article:{article_id}"


def _serialize_article(article: Any) -> dict:
    if isinstance(article, dict):
        return article
    return ArticleOut.from_orm(article).dict()


def get_cached_article(article_id: int) -> Optional[dict]:
    raw = _r.get(cache_key(article_id))
    if not raw:
        return None
    return json.loads(raw)


def set_cached_article(article_id: int, article: Any) -> None:
    payload = _serialize_article(article)
    _r.setex(cache_key(article_id), _TTL, json.dumps(payload, default=str))


def invalidate_article(article_id: int) -> None:
    _r.delete(cache_key(article_id))
