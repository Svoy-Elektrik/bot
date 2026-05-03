import os
import aiohttp
import base64
import json
from typing import Optional

# Конфиги WordPress сайтов (можно несколько)
def get_wp_sites() -> list[dict]:
    """Читаем конфиги WP сайтов из env"""
    sites = []
    # Формат: WP_SITE_1=https://site.com|user|app_password
    i = 1
    while True:
        site_env = os.getenv(f"WP_SITE_{i}")
        if not site_env:
            break
        parts = site_env.split("|")
        if len(parts) == 3:
            sites.append({
                "url": parts[0].rstrip("/"),
                "user": parts[1],
                "password": parts[2],
                "name": f"Site {i}"
            })
        i += 1
    return sites


def get_auth_header(user: str, password: str) -> str:
    credentials = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {credentials}"


async def upload_image_to_wp(site: dict, image_bytes: bytes, filename: str = "seo-image.jpg") -> Optional[int]:
    """Загружаем изображение в медиатеку WP"""
    url = f"{site['url']}/wp-json/wp/v2/media"
    headers = {
        "Authorization": get_auth_header(site["user"], site["password"]),
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=image_bytes) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                return data.get("id")
    return None


async def create_wp_post(
    site: dict,
    title: str,
    content: str,
    excerpt: str = "",
    featured_image_id: Optional[int] = None,
    tags: list[str] = [],
    categories: list[int] = [],
    status: str = "draft"  # draft | publish
) -> Optional[dict]:
    """Создаём пост в WordPress"""
    url = f"{site['url']}/wp-json/wp/v2/posts"
    headers = {
        "Authorization": get_auth_header(site["user"], site["password"]),
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "status": status,
        "format": "standard"
    }

    if featured_image_id:
        payload["featured_media"] = featured_image_id
    if categories:
        payload["categories"] = categories

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status in (200, 201):
                return await resp.json()
    return None


async def get_wp_categories(site: dict) -> list[dict]:
    """Получаем список категорий WP"""
    url = f"{site['url']}/wp-json/wp/v2/categories?per_page=50"
    headers = {"Authorization": get_auth_header(site["user"], site["password"])}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
    return []


async def markdown_to_html(text: str) -> str:
    """Конвертируем Markdown в HTML для WP"""
    import re
    # Заголовки
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    # Жирный и курсив
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Параграфы
    paragraphs = text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h'):
            p = f'<p>{p}</p>'
        result.append(p)
    return '\n'.join(result)
