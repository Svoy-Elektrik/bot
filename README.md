# Article Generator Bot

Telegram-бот, который генерирует статьи через Claude API и публикует их в WordPress, Telegram-канал, или отдаёт текст для копирования.

Реализован на **Next.js 15 + Telegraf 4 + TypeScript**. Telegram-обновления приходят через webhook на `/api/telegram`.

## Поток

`/start` → выбор языка (RU / DE) → выбор длины (1000 / 2000 / 3000 / 5000 символов) → ввод темы → генерация → меню «Куда опубликовать?» (WordPress / Telegram / Скопировать).

## Стек

- Next.js 15 (App Router, webhook endpoint)
- Telegraf 4 + WizardScene (FSM)
- Anthropic SDK (Claude API)
- Node.js fetch (WordPress REST)

## Локальный запуск

```bash
npm install
cp .env.example .env.local
# заполни BOT_TOKEN и CLAUDE_API_KEY
npm run dev
```

Для локального тестирования webhook используй [ngrok](https://ngrok.com):
```bash
ngrok http 3000
# скопируй https-адрес, добавь в .env.local:
# WEBHOOK_URL=https://xxxx.ngrok.io
```

## Деплой на Railway

1. Railway → New Project → Deploy from GitHub → выбери `Svoy-Elektrik/bot`
2. Railway определит Node.js автоматически
3. **Build command**: `npm run build`
4. **Start command**: `npm run start`
5. В **Variables** добавь как минимум:
   - `BOT_TOKEN`
   - `CLAUDE_API_KEY`
6. Опционально:
   - `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_DEFAULT_STATUS`
   - `TG_CHANNEL_ID`
7. `WEBHOOK_URL` **не нужен** — Railway устанавливает `RAILWAY_PUBLIC_DOMAIN` автоматически

## Структура

```
src/
├── instrumentation.ts          # регистрирует webhook при старте сервера
├── app/
│   ├── api/telegram/route.ts   # webhook endpoint POST /api/telegram
│   ├── layout.tsx
│   └── page.tsx
└── lib/
    ├── bot.ts                  # Telegraf singleton + webhook setup
    ├── keyboards.ts            # inline-клавиатуры
    ├── utils.ts                # split_for_telegram
    ├── scenes/
    │   └── article.ts          # WizardScene (FSM: 5 шагов)
    └── services/
        ├── claude.ts           # вызов Anthropic API
        ├── wordpress.ts        # POST /wp-json/wp/v2/posts
        └── telegram_publish.ts # отправка в канал
```
