import os

import anthropic

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

LANG_NAMES = {"ru": "русский", "de": "немецкий"}

SYSTEM_PROMPT = (
    "Ты профессиональный копирайтер. Пишешь живые, структурированные статьи для блога. "
    "Используешь подзаголовки, списки где уместно, и подбираешь подходящий тон под тему. "
    "В конце статьи добавляешь блок из 5-8 хэштегов на том же языке что и статья."
)


def generate_article(topic: str, length: int, lang: str = "ru") -> str:
    lang_name = LANG_NAMES.get(lang, "русский")
    user_prompt = (
        f"Напиши статью на языке: {lang_name}.\n"
        f"Тема: {topic}.\n"
        f"Объём: примерно {length} символов (без учёта хэштегов).\n"
        f"В конце добавь блок из 5–8 хэштегов через пробел, начинающихся с #."
    )
    # Conservative token cap; ~3 chars per token + headroom for hashtags.
    max_tokens = max(800, int(length / 2.5) + 400)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
