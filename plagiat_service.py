import os
import anthropic
import json

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def check_plagiarism(text: str) -> dict:
    """
    Анализ уникальности текста через Claude (как в RankCraft).
    """
    word_count = len(text.split())

    prompt = f"""Проанализируй следующий текст и дай оценку его уникальности.

Оцени:
1. Уникальность (насколько оригинален текст)
2. Оригинальность подачи (не шаблонные фразы)
3. SEO качество (структура, ключевые слова)
4. Человечность (звучит как человек или как машина)

Текст ({word_count} слов):
---
{text[:3000]}
---

Ответь СТРОГО в формате JSON без markdown:
{{
  "uniqueness": 85,
  "originality": 78,
  "seo_quality": 82,
  "humanity": 75,
  "issues": ["проблема 1", "проблема 2"],
  "recommendations": ["рекомендация 1"],
  "verdict": "Краткий вердикт 1-2 предложения"
}}

Числа от 0 до 100."""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        result_text = message.content[0].text.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(result_text)

        return {
            "unique": data.get("uniqueness", 0),
            "originality": data.get("originality", 0),
            "seo_quality": data.get("seo_quality", 0),
            "humanity": data.get("humanity", 0),
            "issues": data.get("issues", []),
            "recommendations": data.get("recommendations", []),
            "verdict": data.get("verdict", ""),
            "error": None
        }

    except Exception as e:
        return {"error": f"Ошибка анализа: {e}", "unique": None}


async def improve_uniqueness(text: str, score: int) -> str:
    """Улучшаем текст если уникальность низкая"""
    prompt = f"""Текст получил оценку уникальности {score}/100. Улучши его:
- Перефразируй шаблонные выражения
- Добавь конкретику и живые детали  
- Сделай язык естественным
- Сохрани SEO-ключевые слова и структуру

Текст:
{text}

Верни только улучшенный текст."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
