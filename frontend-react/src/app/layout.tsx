import type { Metadata } from 'next'
import './globals.css'
import { Navbar } from '@/components/Navbar'
import { Footer } from '@/components/Footer'

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
      <body className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
        <Navbar />
        <main className="pt-16 flex-grow flex justify-center">
          <div className="w-full max-w-7xl mx-auto">
            {children}
          </div>
        </main>
        <Footer />
      </body>
    </html>
  )
} 