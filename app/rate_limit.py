from __future__ import annotations

import os
from typing import Optional, Any

from fastapi import Request, HTTPException, status
from fastapi.concurrency import run_in_threadpool

import redis  # cliente real

try:
    import fakeredis as FAKE_REDIS
except ImportError:
    FAKE_REDIS = None

from .config import get_settings


WINDOW = int(os.getenv("RL_WINDOW_SECONDS", "60"))
LIMIT = int(os.getenv("RL_LIMIT", "60"))


def _is_true(v: Optional[str]) -> bool:
    return (v or "").lower() in {"1", "true", "yes", "y"}


def _make_client() -> Optional[Any]:
    client: Optional[Any] = None

    if not _is_true(os.getenv("DISABLE_RATE_LIMIT")):
        if _is_true(os.getenv("TESTING")) or _is_true(os.getenv("SKIP_REDIS_HEALTH")):
            if FAKE_REDIS:
                client = FAKE_REDIS.FakeRedis(decode_responses=True)
        else:
            settings = get_settings()
            url = getattr(settings, "REDIS_URL", None)
            if url:
                if str(url).startswith("fakeredis://") and FAKE_REDIS:
                    client = FAKE_REDIS.FakeRedis(decode_responses=True)
                else:
                    client = redis.from_url(url, decode_responses=True)
            else:
                host = getattr(settings, "REDIS_HOST", None)
                if host:
                    client = redis.Redis(
                        host=host,
                        port=getattr(settings, "REDIS_PORT", 6379),
                        db=getattr(settings, "REDIS_DB", 0),
                        decode_responses=True,
                    )

    return client


_r = _make_client()


async def rate_limiter(request: Request):
    if _r is None:
        return

    api_key = request.headers.get("x-api-key") or request.client.host
    key = f"rl:{api_key}"

    # INCR y TTL en la ventana
    current = await run_in_threadpool(_r.incr, key)
    if current == 1:
        await run_in_threadpool(_r.expire, key, WINDOW)

    if current > LIMIT:
        ttl = await run_in_threadpool(_r.ttl, key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {ttl}s",
        )
