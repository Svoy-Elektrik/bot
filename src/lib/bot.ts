import { Telegraf, Scenes, session } from 'telegraf'
import { articleWizard } from './scenes/article'

export interface ArticleWizardSession extends Scenes.WizardSessionData {
  lang?: string
  length?: number
  topic?: string
  article?: string
}

export type BotContext = Scenes.WizardContext<ArticleWizardSession>

function createBot(): Telegraf<BotContext> {
  const token = process.env.BOT_TOKEN
  if (!token) throw new Error('BOT_TOKEN is not set')

  const bot = new Telegraf<BotContext>(token)
  const stage = new Scenes.Stage<BotContext>([articleWizard])

  bot.use(session())
  bot.use(stage.middleware())

  bot.start((ctx) => ctx.scene.enter('article'))

  // Fallback for stale callback buttons (e.g. after bot restart)
  bot.on('callback_query', async (ctx) => {
    await ctx.answerCbQuery('Начни заново: /start').catch(() => {})
  })

  return bot
}

// Singleton — survives Next.js hot-reload in development
declare global {
  // eslint-disable-next-line no-var
  var __telegrafBot: Telegraf<BotContext> | undefined
}

export const bot =
  globalThis.__telegrafBot ?? (globalThis.__telegrafBot = createBot())

export async function setupWebhook(): Promise<void> {
  const domain =
    process.env.WEBHOOK_URL ??
    (process.env.RAILWAY_PUBLIC_DOMAIN
      ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}`
      : undefined)

  if (!domain) {
    console.warn('[bot] No WEBHOOK_URL or RAILWAY_PUBLIC_DOMAIN — webhook not registered')
    return
  }

  const url = `${domain}/api/telegram`
  await bot.telegram.setWebhook(url)
  console.log(`[bot] Webhook registered: ${url}`)
}
