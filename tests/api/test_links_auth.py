from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def register_authenticated_user(client):
    login = f"testuser{uuid4().hex[:6]}"
    password = "testpass123"

    register_response = client.post(
        "/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )

    assert register_response.status_code == 200
    assert register_response.cookies.get("session_id")

    me_response = client.get("/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["user_id"]

    return {
        "login": login,
        "password": password,
        "user_id": me_response.json()["user_id"],
    }


def create_authenticated_link(
    client,
    original_url="https://google.com",
    alias="google",
    expires_at="2030-01-01T00:00:00",
):
    shorten_response = client.post(
        "/links/shorten",
        json={
            "original_url": original_url,
            "custom_alias": alias,
            "expires_at": expires_at,
        },
    )

    assert shorten_response.status_code == 200
    assert shorten_response.json()["short_code"] == alias

    short_code = shorten_response.json()["short_code"]
    short_url = f"http://testserver/{short_code}"
    print(f"short url: {short_url}")

    return {
        "short_code": short_code,
        "short_url": short_url,
        "original_url": original_url,
        "alias": alias,
        "expires_at": expires_at,
    }


def test_shorten_with_google_alias_and_expires_at_as_authenticated_user(client):
    register_authenticated_user(client)

    link = create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
        expires_at="2030-01-01T00:00:00",
    )

    assert link["short_code"] == "google"
    assert link["alias"] == "google"

    stats_response = client.get("/links/google/stats")

    assert stats_response.status_code == 200
    assert stats_response.json()["original_url"] == "https://google.com"
    assert stats_response.json()["created_at"] is not None
    assert stats_response.json()["clicks"] == 0


def test_redirect_by_google_alias_returns_302_and_google_location(client):
    register_authenticated_user(client)

    create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    redirect_response = client.get(
        "/google",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == "https://google.com"


def test_search_returns_only_google_link_for_authenticated_user(client):
    register_authenticated_user(client)

    google_link = create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    create_authenticated_link(
        client,
        original_url="https://github.com",
        alias="github",
    )

    search_response = client.get(
        "/links/search",
        params={"fragment": "google.com"},
    )

    assert search_response.status_code == 200
    assert google_link["alias"] in search_response.text
    assert "https://google.com" in search_response.text
    assert "github" not in search_response.text
    assert "https://github.com" not in search_response.text


def test_stats_returns_link_info_for_google_alias_as_authenticated_user(client):
    register_authenticated_user(client)

    create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    stats_response = client.get("/links/google/stats")

    assert stats_response.status_code == 200
    assert stats_response.json()["original_url"] == "https://google.com"
    assert stats_response.json()["created_at"] is not None
    assert stats_response.json()["clicks"] == 0
    assert "last_accessed" in stats_response.json()


def test_update_changes_original_url_for_google_alias_as_authenticated_user(client):
    register_authenticated_user(client)

    create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    update_response = client.put(
        "/links/google",
        json={"original_url": "https://www.google.com"},
    )

    assert update_response.status_code == 200
    assert update_response.json() == {"status": "updated"}

    stats_response = client.get("/links/google/stats")

    assert stats_response.status_code == 200
    assert stats_response.json()["original_url"] == "https://www.google.com"


def test_delete_removes_google_alias_for_authenticated_user(client):
    register_authenticated_user(client)

    create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    delete_response = client.delete("/links/google")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "deleted"}

    stats_response = client.get("/links/google/stats")

    assert stats_response.status_code == 404


def test_search_does_not_return_google_link_of_other_user(client):
    register_authenticated_user(client)

    first_user_link = create_authenticated_link(
        client,
        original_url="https://google.com",
        alias="google",
    )

    second_client = TestClient(app)
    register_authenticated_user(second_client)

    second_user_response = second_client.get(
        "/links/search",
        params={"fragment": "google.com"},
    )

    assert second_user_response.status_code == 200
    assert first_user_link["alias"] not in second_user_response.text
    assert "https://google.com" not in second_user_response.text
