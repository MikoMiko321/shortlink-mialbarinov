import httpx

from app.auth.service import get_current_user_optional
from app.main import app


def test_shorten_redirects_to_google_and_returns_200(client):
    app.dependency_overrides[get_current_user_optional] = lambda: None

    try:
        shorten_response = client.post(
            "/links/shorten",
            json={
                "original_url": "https://google.com",
                "custom_alias": None,
                "expires_at": None,
            },
        )

        assert shorten_response.status_code == 200

        short_code = shorten_response.json()["short_code"]
        short_url = f"http://testserver/{short_code}"
        print(f"short url: {short_url}")

        redirect_response = client.get(f"/{short_code}", follow_redirects=False)

        assert redirect_response.status_code == 302
        assert redirect_response.headers["location"] == "https://google.com"

        final_response = httpx.get(
            redirect_response.headers["location"],
            follow_redirects=True,
            timeout=10.0,
        )

        assert final_response.status_code == 200

    finally:
        app.dependency_overrides.clear()
