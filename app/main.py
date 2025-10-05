from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

# Third-party imports (before local)
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import redis
from redis.exceptions import RedisError

# Local imports
from .db.db import Base, engine
from .routers import articles
from .config import get_settings


app = FastAPI(title="ArticleHub API", version="0.1.0")


# ✅ Create all tables if they don’t exist (safety net)
@app.on_event("startup")
async def _create_tables_on_startup() -> None:
    from . import models  # noqa: F401  # pylint: disable=import-outside-toplevel, unused-import
    await run_in_threadpool(Base.metadata.create_all, engine)


# Routes
app.include_router(articles.router)


@app.get("/health")
async def health():
    status: dict[str, bool] = {}

    # Database health check
    try:
        await run_in_threadpool(lambda: engine.connect().execute(text("SELECT 1")))
        status["db"] = True
    except SQLAlchemyError:
        status["db"] = False

    # Redis health check
    settings = get_settings()
    try:
        await run_in_threadpool(
            lambda: redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
            ).ping()
        )
        status["redis"] = True
    except RedisError:
        status["redis"] = False

    # Global service status
    status["status"] = bool(status.get("db") and status.get("redis"))
    return status
