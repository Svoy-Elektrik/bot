import { Scenes } from 'telegraf'
import type { BotContext } from '../bot'
import { langKeyboard, lengthKeyboard, outputKeyboard } from '../keyboards'
import { generateArticle } from '../services/claude'
import { publishToWordPress, WordPressNotConfigured } from '../services/wordpress'
import { publishToTelegram, TelegramChannelNotConfigured } from '../services/telegram_publish'
import { splitForTelegram } from '../utils'

export const articleWizard = new Scenes.WizardScene<BotContext>(
  'article',

  // Step 0: show language selection
  async (ctx) => {
    await ctx.reply('Выбери язык статьи:', langKeyboard())
    return ctx.wizard.next()
  },

  // Step 1: receive language → show length selection
  async (ctx) => {
    if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) {
      await ctx.reply('Нажми кнопку для выбора языка.')
      return
    }
    const data = ctx.callbackQuery.data
    if (!data.startsWith('lang:')) return
    ctx.scene.session.lang = data.slice(5)
    await ctx.answerCbQuery()
    await ctx.editMessageText('Выбери длину статьи:', lengthKeyboard())
    return ctx.wizard.next()
  },

  // Step 2: receive length → ask for topic
  async (ctx) => {
    if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) {
      await ctx.reply('Нажми кнопку для выбора длины.')
      return
    }
    const data = ctx.callbackQuery.data
    if (!data.startsWith('len:')) return
    ctx.scene.session.length = Number(data.slice(4))
    await ctx.answerCbQuery()
    await ctx.editMessageText('Введи тему статьи:')
    return ctx.wizard.next()
  },

  // Step 3: receive topic → generate article
  async (ctx) => {
    if (!ctx.message || !('text' in ctx.message)) {
      await ctx.reply('Введи тему текстом.')
      return
    }
    const topic = ctx.message.text
    ctx.scene.session.topic = topic

    const loadingMsg = await ctx.reply('⏳ Генерирую статью…')

    try {
      const { lang = 'ru', length = 1000 } = ctx.scene.session
      const article = await generateArticle(topic, length, lang as 'ru' | 'de')
      ctx.scene.session.article = article

      try {
        await ctx.deleteMessage(loadingMsg.message_id)
      } catch {}

      for (const chunk of splitForTelegram(article)) {
        await ctx.reply(chunk)
      }

      await ctx.reply('Куда опубликовать?', outputKeyboard())
      return ctx.wizard.next()
    } catch (err) {
      console.error('[article wizard] generate error:', err)
      await ctx.reply('❌ Ошибка генерации. Попробуй снова: /start')
      return ctx.scene.leave()
    }
  },

  // Step 4: handle output choice
  async (ctx) => {
    if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return

    const data = ctx.callbackQuery.data
    const article = ctx.scene.session.article ?? ''
    const topic = ctx.scene.session.topic ?? 'Статья'

    if (data === 'restart') {
      await ctx.answerCbQuery()
      return ctx.scene.reenter()
    }

    if (data === 'out:copy') {
      await ctx.answerCbQuery('Статья уже выше — просто скопируй 👆')
      await ctx.reply('Нажми /start для новой статьи.')
      return ctx.scene.leave()
    }

    if (data === 'out:wp') {
      try {
        const url = await publishToWordPress(topic, article)
        await ctx.answerCbQuery()
        await ctx.reply(`✅ Опубликовано в WordPress: ${url}`)
      } catch (e) {
        await ctx.answerCbQuery()
        if (e instanceof WordPressNotConfigured) {
          await ctx.reply('⚠️ WordPress не настроен. Задай WP_URL, WP_USER, WP_APP_PASSWORD.')
        } else {
          await ctx.reply(`❌ Ошибка WordPress: ${(e as Error).message}`)
        }
      }
      return ctx.scene.leave()
    }

    if (data === 'out:tg') {
      try {
        await publishToTelegram(ctx.telegram, article)
        await ctx.answerCbQuery()
        await ctx.reply('✅ Опубликовано в Telegram-канал!')
      } catch (e) {
        await ctx.answerCbQuery()
        if (e instanceof TelegramChannelNotConfigured) {
          await ctx.reply('⚠️ Telegram-канал не настроен. Задай TG_CHANNEL_ID и добавь бота в канал.')
        } else {
          await ctx.reply(`❌ Ошибка публикации: ${(e as Error).message}`)
        }
      }
      return ctx.scene.leave()
    }
  },
)
