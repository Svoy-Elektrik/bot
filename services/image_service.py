import os
import aiohttp

IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def generate_image_ideogram(prompt: str) -> bytes | None:
    if not IDEOGRAM_API_KEY:
        return None
    url = "https://api.ideogram.ai/generate"
    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": "ASPECT_16_9",
            "model": "V_2",
            "magic_prompt_option": "AUTO"
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                image_url = data["data"][0]["url"]
                async with session.get(image_url) as img_resp:
                    return await img_resp.read()
    return None

async def generate_image_dalle(prompt: str) -> bytes | None:
    if not OPENAI_API_KEY:
        return None
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1792x1024",
        "response_format": "url"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                image_url = data["data"][0]["url"]
                async with session.get(image_url) as img_resp:
                    return await img_resp.read()
    return None

async def generate_image(prompt: str, style_hint: str = "professional blog") -> bytes | None:
    full_prompt = f"{prompt}, {style_hint}, high quality, sharp, 4k"
    img = await generate_image_ideogram(full_prompt)
    if img:
        return img
    img = await generate_image_dalle(full_prompt)
    return img
