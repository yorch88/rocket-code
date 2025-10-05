import pytest
import fakeredis

pytestmark = pytest.mark.unit

# --- Mock global de Redis para evitar dependencia externa en tests ---
@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
    """
    Reemplaza los clientes Redis globales usados por la app por un FakeRedis en memoria.
    Cubre tanto app.cache._r como app.rate_limit._r (si existe).
    """
    from app import cache as app_cache
    fr = fakeredis.FakeRedis(decode_responses=True)

    # cache.py usa una variable global _r
    monkeypatch.setattr(app_cache, "_r", fr, raising=True)

    # rate_limit.py también usa _r; si no ha sido importado aún, no pasa nada.
    try:
        from app import rate_limit as app_rate_limit
        if hasattr(app_rate_limit, "_r"):
            monkeypatch.setattr(app_rate_limit, "_r", fr, raising=True)
    except Exception:
        # Si el módulo no existe en este proyecto o no se usa en estos tests, lo ignoramos.
        pass

    yield
    fr.flushall()


def test_list_articles_delegates_to_repo(monkeypatch):
    from app.services import articles as svc

    called = {}

    def fake_repo_list_articles(db, filters):
        called["args"] = (db, filters)
        return (["a1", "a2"], 2)

    monkeypatch.setattr("app.repositories.articles.list_articles", fake_repo_list_articles)

    items, total = svc.list_articles(None, page=1, page_size=10, author=None, tag=None, order="desc")

    assert items == ["a1", "a2"]
    assert total == 2

    filters = called["args"][1]
    assert filters.page == 1
    assert filters.page_size == 10
    assert filters.order == "desc"
<<<<<<< HEAD

=======
>>>>>>> e7b31fc020576c5c1dfdb5b9cb73b10cab5f4868

def test_create_article_delegates_to_repo(monkeypatch):
    from app.services import articles as svc

    payload_in = {"title": "t", "body": "b", "tags": "dev", "author": "me"}
    fake_created = {"id": 123, **payload_in}

<<<<<<< HEAD
    def fake_repo_create
=======
    def fake_repo_create_article(db, data):
        assert "title" in data and data["title"] == "t"
        return fake_created

    monkeypatch.setattr("app.repositories.articles.create_article", fake_repo_create_article)

    created = svc.create_article(None, payload_in)

    assert created["id"] == 123
    assert created["title"] == "t"
>>>>>>> e7b31fc020576c5c1dfdb5b9cb73b10cab5f4868
