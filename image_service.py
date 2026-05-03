import aiohttp
import urllib.parse

# Pollinations.ai — бесплатно, без ключей (как в RankCraft)


async def generate_image(prompt: str, style: str = "professional", size: str = "1280x720") -> bytes | None:
    """Генерация изображения через Pollinations.ai — бесплатно, без регистрации"""
    width, height = size.split("x") if "x" in size else ("1280", "720")

    style_hints = {
        "professional": "professional photography, sharp, 4k, high quality",
        "flat":         "flat illustration, vector art, clean design",
        "3d":           "3D render, Cinema4D, octane render, realistic",
        "dark":         "dark premium, dramatic lighting, cinematic",
        "minimal":      "minimalist, white background, clean, modern"
    }
    style_suffix = style_hints.get(style, style_hints["professional"])
    full_prompt = f"{prompt}, {style_suffix}"

    encoded = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as e:
        print(f"Pollinations error: {e}")
    return None


async def generate_og_image(title: str, style: str = "business") -> bytes | None:
    """OG изображение для статьи / соцсетей"""
    style_map = {
        "business": "corporate, professional, office, business",
        "tech":     "futuristic, technology, data, neon, modern",
        "minimal":  "minimalist, white, clean, typography",
        "vibrant":  "vibrant colors, creative, eye-catching",
        "dark":     "dark background, premium, luxury"
    }
    prompt = f"{title}, {style_map.get(style, style_map['business'])}, blog header image"
    return await generate_image(prompt, size="1280x720")


async def generate_article_image(topic: str, style: str = "photo") -> bytes | None:
    """Изображение для SEO статьи"""
    style_map = {
        "photo":      "photorealistic, stock photo quality",
        "flat":       "flat illustration, infographic style",
        "3d":         "3D render, isometric",
        "watercolor": "watercolor painting, artistic"
    }
    prompt = f"{topic}, {style_map.get(style, style_map['photo'])}, article hero image"
    return await generate_image(prompt, size="1280x720")
