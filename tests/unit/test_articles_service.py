import pytest

pytestmark = pytest.mark.unit

def test_list_articles_delegates_to_repo(monkeypatch):
    from app.services import articles as svc

    called = {}
    def fake_repo_list_articles(db, **kw):
        called["args"] = (db,)
        called["kwargs"] = kw
        # simulamos retorno de objetos Article (o dicts)
        return (["a1", "a2"], 2)

    # parcheamos la función del repo usada por el servicio
    monkeypatch.setattr("app.repositories.articles.list_articles", fake_repo_list_articles)

    # llamamos al servicio (db puede ser None en unit)
    items, total = svc.list_articles(None, page=1, page_size=10, author=None, tag=None, order="desc")

    assert items == ["a1", "a2"]
    assert total == 2
    # el servicio debe pasar los parámetros al repo correctamente
    assert called["kwargs"]["page"] == 1
    assert called["kwargs"]["page_size"] == 10
    assert called["kwargs"]["order"] == "desc"


def test_create_article_delegates_to_repo(monkeypatch):
    from app.services import articles as svc

    payload_in = {"title": "t", "body": "b", "tags": "dev", "author": "me"}
    fake_created = {"id": 123, **payload_in}

    def fake_repo_create_article(db, data):
        # afirmaciones internas de validación básica
        assert "title" in data and data["title"] == "t"
        return fake_created

    monkeypatch.setattr("app.repositories.articles.create_article", fake_repo_create_article)

    created = svc.create_article(None, payload_in)

    assert created["id"] == 123
    assert created["title"] == "t"
