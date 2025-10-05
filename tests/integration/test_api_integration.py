import os
import time
import requests
import pytest

pytestmark = pytest.mark.integration

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("IT_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def api_key() -> str:
    return os.getenv("IT_API_KEY", os.getenv("API_KEY", "47da9ef4-0a22-4625-89f3-ef7025a64192"))

@pytest.fixture(scope="session")
def headers(api_key) -> dict:
    return {"x-api-key": api_key}

def _wait_for_ready(base_url: str, timeout: int = 30) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{base_url}/health", timeout=2)
            if r.ok and r.json().get("status") is not False:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="session", autouse=True)
def ensure_service_ready(base_url):
    if not _wait_for_ready(base_url):
        pytest.skip("Service not ready on /health; skipping integration tests.")

def test_end_to_end_crud(base_url, headers, ensure_service_ready):
    article_id = None
    try:
        # ---------- Arrange ----------
        create_payload = {"title": "Int Test", "body": "Body", "tags": ["int"], "author": "QA"}

        # ---------- Act ----------
        r = requests.post(f"{base_url}/articles", json=create_payload, headers=headers, timeout=5)

        # ---------- Assert ----------
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["title"] == "Int Test"
        article_id = body["id"]

        # ---------- Arrange ----------
        # (no extra arrange; just the id)
        # ---------- Act ----------
        r = requests.get(f"{base_url}/articles/{article_id}", headers=headers, timeout=5)

        # ---------- Assert ----------
        assert r.status_code == 200, r.text
        assert r.json()["title"] == "Int Test"

        # ---------- Arrange ----------
        update_payload = {"title": "Updated"}
        # ---------- Act ----------
        r = requests.put(f"{base_url}/articles/{article_id}", json=update_payload, headers=headers, timeout=5)

        # ---------- Assert ----------
        assert r.status_code == 200, r.text
        assert r.json()["title"] == "Updated"

        # ---------- Arrange ----------
        list_params = {"author": "QA"}
        # ---------- Act ----------
        r = requests.get(f"{base_url}/articles", params=list_params, headers=headers, timeout=5)

        # ---------- Assert ----------
        assert r.status_code == 200, r.text
        ids = [it["id"] for it in r.json()]
        assert article_id in ids

        # ---------- Arrange ----------
        search_params = {"q": "Updated"}
        # ---------- Act ----------
        r = requests.get(f"{base_url}/articles/search", params=search_params, headers=headers, timeout=5)

        # ---------- Assert ----------
        assert r.status_code == 200, r.text
        assert any(it["id"] == article_id for it in r.json())

    finally:
        # Best-effort cleanup (does not fail test if delete fails)
        if article_id is not None:
            try:
                requests.delete(f"{base_url}/articles/{article_id}", headers=headers, timeout=5)
            except Exception:
                pass
