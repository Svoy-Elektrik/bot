import os
import aiohttp
import asyncio

TEXTRU_KEY = os.getenv("TEXTRU_API_KEY")


async def check_plagiarism(text: str) -> dict:
    """Проверка уникальности через Text.ru API"""
    if not TEXTRU_KEY:
        return {"error": "Text.ru API ключ не настроен", "unique": None}

    # Шаг 1: Отправляем текст на проверку
    async with aiohttp.ClientSession() as session:
        # Создаём задачу проверки
        add_url = "https://api.text.ru/post"
        add_data = {
            "text": text,
            "userkey": TEXTRU_KEY,
            "jsonvisible": "detail"
        }

        async with session.post(add_url, data=add_data) as resp:
            result = await resp.json()
            if "error_code" in result:
                return {"error": f"Ошибка Text.ru: {result.get('error_desc', 'неизвестно')}", "unique": None}

            uid = result.get("text_uid")
            if not uid:
                return {"error": "Не удалось получить UID задачи", "unique": None}

        # Шаг 2: Ждём результат (Text.ru асинхронный)
        check_url = "https://api.text.ru/post"
        for attempt in range(20):  # до 2 минут
            await asyncio.sleep(6)
            check_data = {
                "uid": uid,
                "userkey": TEXTRU_KEY,
                "jsonvisible": "detail"
            }
            async with session.post(check_url, data=check_data) as resp:
                data = await resp.json()

                if data.get("text_unique") is not None:
                    unique_pct = float(data["text_unique"])
                    return {
                        "unique": unique_pct,
                        "uid": uid,
                        "report_url": f"https://text.ru/antiplagiat/{uid}",
                        "error": None
                    }

                if data.get("error_code") == "181":
                    # Ещё в обработке
                    continue

                break

        return {"error": "Таймаут проверки", "unique": None}
