export class WordPressNotConfigured extends Error {
  constructor() {
    super('WordPress credentials not configured')
  }
}

export async function publishToWordPress(
  title: string,
  content: string,
  status = process.env.WP_DEFAULT_STATUS ?? 'draft',
): Promise<string> {
  const url = process.env.WP_URL
  const user = process.env.WP_USER
  const password = process.env.WP_APP_PASSWORD

  if (!url || !user || !password) throw new WordPressNotConfigured()

  const credentials = Buffer.from(`${user}:${password}`).toString('base64')

  const response = await fetch(`${url}/wp-json/wp/v2/posts`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${credentials}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, content, status }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`WordPress API error ${response.status}: ${error}`)
  }

  const post = (await response.json()) as { link: string }
  return post.link
}
