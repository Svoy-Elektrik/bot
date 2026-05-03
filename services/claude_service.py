import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def generate_seo_article(topic: str, keywords: str, language: str = "ru") -> str:
    """Генерация SEO статьи через Claude"""
    prompt = f"""Напиши профессиональную SEO статью на тему: "{topic}"

Ключевые слова: {keywords}
Язык: {language}

Структура:
- SEO заголовок H1 (с главным ключевым словом)
- Мета-описание (150-160 символов)
- Введение (100-150 слов)
- 3-5 разделов H2 с подзаголовками H3
- Каждый раздел 200-300 слов
- Заключение с призывом к действию
- Плотность ключевых слов: 1.5-2.5%

Требования:
- Уникальный, живой текст без воды
- Естественное вхождение ключевых слов
- LSI-слова и синонимы
- Структурированный, легко читаемый текст
- Форматирование в Markdown"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


async def rewrite_text(text: str) -> str:
    """Рерайт и уникализация текста"""
    prompt = f"""Сделай глубокий рерайт следующего текста. 

Требования:
- Сохрани смысл и все факты
- Измени структуру предложений
- Используй синонимы
- Уникальность должна быть выше 90%
- Текст должен звучать естественно
- Сохрани SEO-оптимизацию

Исходный текст:
{text}"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


async def generate_meta(topic: str, keywords: str) -> str:
    """Генерация мета-тегов"""
    prompt = f"""Создай SEO мета-теги для страницы:
Тема: {topic}
Ключевые слова: {keywords}

Верни в формате:
TITLE: (до 60 символов)
DESCRIPTION: (150-160 символов)
KEYWORDS: (5-7 ключевых слов через запятую)
OG_TITLE: (для соцсетей)
OG_DESCRIPTION: (для соцсетей)"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


async def generate_channel_post(topic: str, article_url: str = "") -> str:
    """Генерация поста для Telegram канала"""
    prompt = f"""Напиши engaging пост для Telegram канала на тему: "{topic}"
{"Ссылка на статью: " + article_url if article_url else ""}

Требования:
- 150-300 символов
- Цепляющий заголовок с эмодзи
- Краткая суть (2-3 предложения)
- Призыв к действию
- 3-5 хэштегов
- Форматирование Telegram Markdown"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
