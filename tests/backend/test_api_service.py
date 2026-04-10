import os
import tempfile

from fastapi.testclient import TestClient

# Ensure the service uses a writable temp DB path during tests
os.environ.setdefault("DB_PATH", os.path.join(tempfile.gettempdir(), "test_db.sqlite3"))

from apps.backend.api_service.src.main import app


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert body.get("status") == "healthy"


def test_get_data_returns_list():
    resp = client.get("/data")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
