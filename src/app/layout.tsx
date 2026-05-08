import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Article Generator Bot',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
