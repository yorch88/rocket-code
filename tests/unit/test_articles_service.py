import pytest
import fakeredis

pytestmark = pytest.mark.unit

@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
    from app import cache as app_cache
    fr = fakeredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(app_cache, "_r", fr, raising=True)

    try:
        from app import rate_limit as app_rate_limit
        if hasattr(app_rate_limit, "_r"):
            monkeypatch.setattr(app_rate_limit, "_r", fr, raising=True)
    except Exception:
        pass

    yield
    fr.flushall()


def test_list_articles_delegates_to_repo(monkeypatch):
    # ---------- Arrange ----------
    from app.services import articles as svc

    called = {}

    def fake_repo_list_articles(db, filters):
        called["args"] = (db, filters)
        return (["a1", "a2"], 2)

    monkeypatch.setattr("app.repositories.articles.list_articles", fake_repo_list_articles)

    # ---------- Act ----------
    items, total = svc.list_articles(None, page=1, page_size=10, author=None, tag=None, order="desc")

    # ---------- Assert ----------
    assert items == ["a1", "a2"]
    assert total == 2

    filters = called["args"][1]
    assert filters.page == 1
    assert filters.page_size == 10
    assert filters.order == "desc"


def test_create_article_delegates_to_repo(monkeypatch):
    # ---------- Arrange ----------
    from app.services import articles as svc

    payload_in = {"title": "t", "body": "b", "tags": "dev", "author": "me"}
    fake_created = {"id": 123, **payload_in}

    def fake_repo_create_article(db, data):
        assert "title" in data and data["title"] == "t"
        return fake_created

    monkeypatch.setattr("app.repositories.articles.create_article", fake_repo_create_article)

    # ---------- Act ----------
    created = svc.create_article(None, payload_in)

    # ---------- Assert ----------
    assert created["id"] == 123
    assert created["title"] == "t"
