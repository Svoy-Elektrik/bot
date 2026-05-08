export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { setupWebhook } = await import('./lib/bot')
    await setupWebhook()
  }
}
