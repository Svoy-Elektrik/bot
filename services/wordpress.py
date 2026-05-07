import os
from base64 import b64encode

import requests


class WordPressNotConfigured(Exception):
    """Raised when WP env vars are missing."""


def publish_to_wordpress(title: str, content: str, status: str | None = None) -> str:
    url = os.getenv("WP_URL")
    user = os.getenv("WP_USER")
    app_pwd = os.getenv("WP_APP_PASSWORD")
    if not (url and user and app_pwd):
        raise WordPressNotConfigured()

    status = status or os.getenv("WP_DEFAULT_STATUS", "draft")
    api = url.rstrip("/") + "/wp-json/wp/v2/posts"
    auth = b64encode(f"{user}:{app_pwd}".encode()).decode()

    r = requests.post(
        api,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        json={"title": title, "content": content, "status": status},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("link") or data.get("guid", {}).get("rendered", "")
