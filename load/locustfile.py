import random
import string

from locust import HttpUser, between, tag, task


def rnd(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class ShortlinkUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @tag("create")
    @task(3)
    def create_link(self):
        self.client.post("/links/shorten", json={"original_url": f"https://example.com/{rnd(12)}"})

    @tag("cache")
    @task(1)
    def create_and_redirect(self):
        r = self.client.post("/links/shorten", json={"original_url": f"https://example.com/{rnd(12)}"})
        code = r.json().get("short_code")
        if code:
            self.client.get(f"/{code}", allow_redirects=False)
            self.client.get(f"/{code}", allow_redirects=False)
