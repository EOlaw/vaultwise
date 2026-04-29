import os
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient
from app.app import app


def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
