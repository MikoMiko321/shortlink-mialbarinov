from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.auth.service import get_current_user_optional
from app.database import get_db
from app.main import app

client = TestClient(app)


def test_shorten_returns_short_code(client):
    app.dependency_overrides[get_current_user_optional] = lambda: None

    response = client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": None,
            "expires_at": None,
        },
    )

    assert response.status_code == 200
    assert response.json()["short_code"]

    app.dependency_overrides.clear()
