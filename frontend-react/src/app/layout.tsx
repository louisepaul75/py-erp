import './globals.css'
import type { Metadata } from 'next'
import { Navbar } from '@/components/Navbar'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'pyERP - Enterprise Resource Planning',
  description: 'Modern ERP system built with Python and React',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon.png' }
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-amber-950/90 text-amber-50">
        <Navbar />
        <main className="pt-16 pb-[calc(var(--footer-height,2.75rem)+0.5rem)] flex-grow flex justify-center">
          <div className="w-full max-w-7xl mx-auto">
            {children}
          </div>
        </main>
        <Footer />
      </body>
    </html>
  )
} 