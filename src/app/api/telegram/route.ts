import { NextRequest, NextResponse } from 'next/server'
import { bot } from '@/lib/bot'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    await bot.handleUpdate(body)
  } catch (error) {
    console.error('[telegram webhook]', error)
  }
  // Always return 200 — Telegram retries on 5xx
  return NextResponse.json({ ok: true })
}
