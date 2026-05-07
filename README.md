# Article Generator Bot

Telegram-бот, который генерирует статьи через Claude API и публикует их в WordPress, в Telegram-канал, или просто отдаёт текст для копирования.

## Поток

`/start` → выбор языка (RU / DE) → выбор длины (1000 / 2000 / 3000 / 5000 символов) → ввод темы → бот генерирует статью с хэштегами → меню «Куда выложить?» (WordPress / Telegram / Скопировать).

## Стек

- Python 3.11
- aiogram 3.4 (Telegram bot framework, polling)
- anthropic SDK (Claude API)
- requests (WordPress REST)

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# заполни BOT_TOKEN и CLAUDE_API_KEY минимум
python main.py
```

## Деплой на Railway

1. Зарегистрируйся на https://railway.app, привяжи GitHub.
2. **New Project → Deploy from GitHub repo** → выбери `Svoy-Elektrik/bot`.
3. Railway увидит `Procfile` (`worker: python main.py`) и `.python-version` — соберёт автоматически.
4. В **Variables** добавь как минимум:
   - `BOT_TOKEN`
   - `CLAUDE_API_KEY`
5. Опционально:
   - `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_DEFAULT_STATUS`
   - `TG_CHANNEL_ID`
6. Каждый push в `main` → автодеплой.

## Настройка WordPress (Application Passwords)

1. Войти в WP Admin → **Users → Profile**.
2. Прокрутить до **Application Passwords**, ввести имя «Article Bot», нажать **Add New Application Password**.
3. Скопировать сгенерированный пароль (показывается один раз) в `WP_APP_PASSWORD`.
4. `WP_USER` — это твой WordPress-логин (не email).

Бот публикует через `POST /wp-json/wp/v2/posts`. По умолчанию `status=draft` — посты появятся как черновики, ты их вручную опубликуешь. Чтобы публиковать сразу, поставь `WP_DEFAULT_STATUS=publish`.

## Настройка Telegram-канала

1. Создай канал, добавь бота админом с правом отправки сообщений.
2. Отправь любое сообщение в канал, форварднь его боту `@userinfobot` чтобы получить numeric `chat_id` (формата `-1001234567890`).
3. Положи `chat_id` в `TG_CHANNEL_ID` (или используй `@channelusername`).

## Структура

```
bot/
├── main.py              # точка входа, старт polling
├── config.py            # документация переменных окружения
├── states.py            # FSM-состояния
├── keyboards.py         # inline-клавиатуры
├── utils.py             # split_for_telegram
├── handlers/
│   ├── start.py         # /start, callbacks выбора языка/длины/restart
│   ├── generate.py      # обработка темы → генерация
│   ├── output.py        # callbacks WP/TG/copy
│   └── voice.py         # заглушка под голос (не в MVP)
└── services/
    ├── claude.py        # вызов Anthropic API
    ├── wordpress.py     # POST в /wp-json/wp/v2/posts
    └── telegram_publish.py  # публикация в канал
```
