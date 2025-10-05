import os
import time
import requests
import pytest

BASE_URL = os.getenv("IT_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("IT_API_KEY", os.getenv("API_KEY", "47da9ef4-0a22-4625-89f3-ef7025a64192"))

pytestmark = pytest.mark.integration

def wait_for_ready(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.ok and r.json().get("status") is not False:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def test_end_to_end_crud():
    assert wait_for_ready(), "Service not ready on /health"

    headers = {"x-api-key": API_KEY}

    # Create
    payload = {"title":"Int Test","body":"Body","tags":["int"],"author":"QA"}
    r = requests.post(f"{BASE_URL}/articles", json=payload, headers=headers, timeout=5)
    assert r.status_code == 201, r.text
    aid = r.json()["id"]

    # Read
    r = requests.get(f"{BASE_URL}/articles/{aid}", headers=headers, timeout=5)
    assert r.status_code == 200
    assert r.json()["title"] == "Int Test"

    # Update
    r = requests.put(f"{BASE_URL}/articles/{aid}", json={"title":"Updated"}, headers=headers, timeout=5)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"

    # List
    r = requests.get(f"{BASE_URL}/articles", params={"author":"QA"}, headers=headers, timeout=5)
    assert r.status_code == 200
    assert any(item["id"] == aid for item in r.json())

    # Search
    r = requests.get(f"{BASE_URL}/articles/search", params={"q":"Updated"}, headers=headers, timeout=5)
    assert r.status_code == 200

    # Delete
    r = requests.delete(f"{BASE_URL}/articles/{aid}", headers=headers, timeout=5)
    assert r.status_code == 204
