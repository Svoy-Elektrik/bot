import type { Telegram } from 'telegraf'
import { splitForTelegram } from '../utils'

export class TelegramChannelNotConfigured extends Error {
  constructor() {
    super('TG_CHANNEL_ID not configured')
  }
}

export async function publishToTelegram(telegram: Telegram, text: string): Promise<void> {
  const chatId = process.env.TG_CHANNEL_ID
  if (!chatId) throw new TelegramChannelNotConfigured()

  const target: number | string = /^-?\d+$/.test(chatId) ? Number(chatId) : chatId

  for (const chunk of splitForTelegram(text)) {
    await telegram.sendMessage(target, chunk)
  }
}
