import os

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import redis
from redis.exceptions import RedisError

from .db.db import Base, engine
from .routers import articles
from .config import get_settings


def _is_true(v: str | None) -> bool:
    return (v or "").lower() in {"1", "true", "yes", "y"}


def create_app() -> FastAPI:
    application = FastAPI(title="Rocket Article API", version="0.1.0")

    @application.on_event("startup")
    async def _create_tables_on_startup() -> None:
        from . import models  # noqa: F401  # pylint: disable=import-outside-toplevel, unused-import

        await run_in_threadpool(Base.metadata.create_all, engine)

    # Routes
    application.include_router(articles.router)

    @application.get("/health")
    async def health():
        status: dict[str, bool] = {}

        # Database health check (cerrando la conexión correctamente)
        try:
            def _check_db() -> None:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

            await run_in_threadpool(_check_db)
            status["db"] = True
        except SQLAlchemyError:
            status["db"] = False

        # Redis health check (opcional)
        settings = get_settings()
        skip_redis = _is_true(os.getenv("SKIP_REDIS_HEALTH"))
        redis_ok = True

        if not skip_redis:
            try:
                client = None
                # Soporta REDIS_URL o REDIS_HOST/PORT/DB
                if getattr(settings, "REDIS_URL", None):
                    client = redis.from_url(settings.REDIS_URL)
                elif getattr(settings, "REDIS_HOST", None):
                    client = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=getattr(settings, "REDIS_PORT", 6379),
                        db=getattr(settings, "REDIS_DB", 0),
                    )
                # Si no hay config de redis, no lo tomamos como fallo
                if client is not None:
                    await run_in_threadpool(client.ping)
                redis_ok = True
            except RedisError:
                redis_ok = False

        status["redis"] = redis_ok if not skip_redis else True

        # Global service status
        status["status"] = bool(status.get("db") and status.get("redis"))
        return status

    return application


# Export default app for uvicorn and imports in tests
app = create_app()
