import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'pyERP Frontend',
  description: 'React frontend for pyERP system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  )
} 