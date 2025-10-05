import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("TESTING", "1")
os.environ.setdefault("SKIP_REDIS_HEALTH", "1")

from app.main import create_app
app = create_app()

from app.db.db import Base, engine, SessionLocal


from alembic import command
from alembic.config import Config

ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
ALEMBIC_INI_PATH = os.path.abspath(ALEMBIC_INI_PATH)


@pytest.fixture(scope="session", autouse=True)
def _migrated_schema():

    alembic_cfg = Config(ALEMBIC_INI_PATH)

    if os.getenv("DATABASE_URL"):
        alembic_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

    command.upgrade(alembic_cfg, "head")

    yield


@pytest.fixture
def db_session():

    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def _override_get_db(db_session, monkeypatch):

    get_db_target = None

    try:
        from app.db import db as app_db_mod
        if hasattr(app_db_mod, "get_db"):
            get_db_target = app_db_mod.get_db
    except Exception:
        pass

    if get_db_target is None:
        try:
            from app.db import session as app_db_session
            if hasattr(app_db_session, "get_db"):
                get_db_target = app_db_session.get_db
        except Exception:
            pass

    def _test_get_db():
        try:
            yield db_session
        finally:
            pass

    if get_db_target is not None:
        app.dependency_overrides[get_db_target] = _test_get_db


import fakeredis

@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
    fr = fakeredis.FakeRedis(decode_responses=True)

    try:
        from app import cache as app_cache
        if hasattr(app_cache, "_r"):
            monkeypatch.setattr(app_cache, "_r", fr, raising=False)
    except Exception:
        pass

    try:
        from app import rate_limit as app_rate_limit
        if hasattr(app_rate_limit, "_r"):
            monkeypatch.setattr(app_rate_limit, "_r", fr, raising=False)
    except Exception:
        pass

    yield
    try:
        fr.flushall()
    except Exception:
        pass


@pytest.fixture
def client():
    return TestClient(app)
