import { Markup } from 'telegraf'

export function langKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🇷🇺 Русский', 'lang:ru'),
      Markup.button.callback('🇩🇪 Deutsch', 'lang:de'),
    ],
  ])
}

export function lengthKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('1 000', 'len:1000'),
      Markup.button.callback('2 000', 'len:2000'),
    ],
    [
      Markup.button.callback('3 000', 'len:3000'),
      Markup.button.callback('5 000', 'len:5000'),
    ],
  ])
}

export function outputKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📝 WordPress', 'out:wp'),
      Markup.button.callback('📢 Telegram', 'out:tg'),
    ],
    [Markup.button.callback('📋 Скопировать', 'out:copy')],
    [Markup.button.callback('🔄 Новая статья', 'restart')],
  ])
}
