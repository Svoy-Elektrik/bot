export function splitForTelegram(text: string, limit = 4000): string[] {
  if (text.length <= limit) return [text]

  const chunks: string[] = []
  let current = ''

  for (const paragraph of text.split('\n\n')) {
    const addition = current ? '\n\n' + paragraph : paragraph
    if (current.length + addition.length > limit) {
      if (current) chunks.push(current)
      current = paragraph
    } else {
      current += addition
    }
  }

  if (current) chunks.push(current)
  return chunks
}
