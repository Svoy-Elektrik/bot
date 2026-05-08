import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic({ apiKey: process.env.CLAUDE_API_KEY })

const MODEL = process.env.CLAUDE_MODEL ?? 'claude-sonnet-4-6'

const SYSTEM_PROMPT = `Ты профессиональный копирайтер для компании по электромонтажным работам.
Пиши экспертные, полезные статьи. Структурируй текст с заголовками и абзацами.
В конце добавляй 3-5 релевантных хэштегов.`

export async function generateArticle(
  topic: string,
  length: number,
  lang: 'ru' | 'de' = 'ru',
): Promise<string> {
  const maxTokens = Math.max(800, Math.floor(length / 2.5) + 400)
  const langLabel = lang === 'ru' ? 'русском' : 'немецком'

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: maxTokens,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: `Напиши статью на ${langLabel} языке на тему: "${topic}". Объём: около ${length} символов.`,
      },
    ],
  })

  const block = response.content[0]
  if (block.type !== 'text') throw new Error('Unexpected response type from Claude')
  return block.text
}
