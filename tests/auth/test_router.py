from types import SimpleNamespace

import pytest

from app.auth import router as auth_router_module
from app.database import get_db
from app.main import app


@pytest.fixture(autouse=True)
def override_db_dependency():
    fake_db = object()
    app.dependency_overrides[get_db] = lambda: fake_db
    yield fake_db
    app.dependency_overrides.clear()


def test_register_returns_cookie_for_valid_user(client, override_db_dependency, monkeypatch):
    captured = {}

    def fake_create_user(db, login, password):
        captured["db"] = db
        captured["login"] = login
        captured["password"] = password
        return SimpleNamespace(id=123)

    def fake_create_session(user_id):
        captured["user_id"] = user_id
        return "session-123"

    monkeypatch.setattr(auth_router_module, "create_user", fake_create_user)
    monkeypatch.setattr(auth_router_module, "create_session", fake_create_session)

    response = client.post(
        "/auth/register",
        json={
            "login": "testuser",
            "password": "testpass123",
        },
    )

    assert response.status_code == 200
    assert response.text == "registered"
    assert response.cookies.get("session_id") == "session-123"
    assert captured == {
        "db": override_db_dependency,
        "login": "testuser",
        "password": "testpass123",
        "user_id": 123,
    }


def test_register_returns_400_if_user_already_exists(client, monkeypatch):
    def fake_create_user(db, login, password):
        raise ValueError

    monkeypatch.setattr(auth_router_module, "create_user", fake_create_user)

    response = client.post(
        "/auth/register",
        json={
            "login": "testuser",
            "password": "testpass123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "user already exists"}


def test_register_returns_422_if_login_is_missing(client):
    response = client.post(
        "/auth/register",
        json={
            "password": "testpass123",
        },
    )

    assert response.status_code == 422


def test_register_returns_422_if_password_is_missing(client):
    response = client.post(
        "/auth/register",
        json={
            "login": "testuser",
        },
    )

    assert response.status_code == 422


def test_register_returns_422_if_login_is_null(client):
    response = client.post(
        "/auth/register",
        json={
            "login": None,
            "password": "testpass123",
        },
    )

    assert response.status_code == 422


def test_login_returns_cookie_for_valid_credentials(client, override_db_dependency, monkeypatch):
    captured = {}

    def fake_authenticate(db, login, password):
        captured["db"] = db
        captured["login"] = login
        captured["password"] = password
        return SimpleNamespace(id=321)

    def fake_create_session(user_id):
        captured["user_id"] = user_id
        return "session-321"

    monkeypatch.setattr(auth_router_module, "authenticate", fake_authenticate)
    monkeypatch.setattr(auth_router_module, "create_session", fake_create_session)

    response = client.post(
        "/auth/login",
        json={
            "login": "testuser",
            "password": "testpass123",
        },
    )

    assert response.status_code == 200
    assert response.text == "logged in"
    assert response.cookies.get("session_id") == "session-321"
    assert captured == {
        "db": override_db_dependency,
        "login": "testuser",
        "password": "testpass123",
        "user_id": 321,
    }


def test_login_returns_401_for_wrong_credentials(client, monkeypatch):
    def fake_authenticate(db, login, password):
        return None

    monkeypatch.setattr(auth_router_module, "authenticate", fake_authenticate)

    response = client.post(
        "/auth/login",
        json={
            "login": "testuser",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "wrong login or password"}


def test_login_returns_422_if_login_is_missing(client):
    response = client.post(
        "/auth/login",
        json={
            "password": "testpass123",
        },
    )

    assert response.status_code == 422


def test_login_returns_422_if_password_is_missing(client):
    response = client.post(
        "/auth/login",
        json={
            "login": "testuser",
        },
    )

    assert response.status_code == 422


def test_login_returns_422_if_password_is_null(client):
    response = client.post(
        "/auth/login",
        json={
            "login": "testuser",
            "password": None,
        },
    )

    assert response.status_code == 422


def test_me_returns_user_id_for_valid_session(client, monkeypatch):
    captured = {}

    def fake_get_user_by_session(session_id):
        captured["session_id"] = session_id
        return 777

    monkeypatch.setattr(auth_router_module, "get_user_by_session", fake_get_user_by_session)

    response = client.get(
        "/auth/me",
        cookies={"session_id": "valid-session"},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": 777}
    assert captured["session_id"] == "valid-session"


def test_me_returns_401_without_session_cookie(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_401_for_invalid_session(client, monkeypatch):
    def fake_get_user_by_session(session_id):
        return None

    monkeypatch.setattr(auth_router_module, "get_user_by_session", fake_get_user_by_session)

    response = client.get(
        "/auth/me",
        cookies={"session_id": "invalid-session"},
    )

    assert response.status_code == 401
