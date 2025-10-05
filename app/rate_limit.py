from fastapi.concurrency import run_in_threadpool
from fastapi import Request, HTTPException, status
import redis
from .config import get_settings

s = get_settings()
_r = redis.Redis(host=s.REDIS_HOST, port=s.REDIS_PORT, db=s.REDIS_DB, decode_responses=True)
WINDOW = 60
LIMIT = 60

async def rate_limiter(request: Request):
    api_key = request.headers.get("x-api-key") or request.client.host
    key = f"rl:{api_key}"
    current = await run_in_threadpool(_r.incr, key)
    if current == 1:
        await run_in_threadpool(_r.expire, key, WINDOW)
    if current > LIMIT:
        ttl = await run_in_threadpool(_r.ttl, key)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Rate limit exceeded. Try again in {ttl}s")
