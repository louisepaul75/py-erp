import './globals.css'
import type { Metadata, Viewport } from 'next'
import { Footer } from '@/components/Footer'
import { Providers } from './providers'
import MainLayout from '@/components/layout/MainLayout'
import { LastVisitedProvider } from '@/context/LastVisitedContext'
import { ThemeProvider } from 'next-themes'
import { CommandMenu } from '@/components/command/CommandMenu'
// import { Theme } from '@radix-ui/themes';

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

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

// Default language is German
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" suppressHydrationWarning>
      <head>
        {/* Add Google Font links */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin={"anonymous"} />
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@700&family=PT+Serif:wght@700&display=swap" rel="stylesheet" />
        {/* Add empty CSRF token meta tag that can be populated by API responses */}
        <meta name="csrf-token" content="" />
      </head>
      {/* Make body a flex container, column direction */}
      <body className="min-h-screen bg-gray-50 text-amber-950 flex flex-col">
        {/* Add texture div (will be visually controlled by CSS) */}
        <div className="texture" />
        <ThemeProvider attribute="data-theme" defaultTheme="default-light">
          <Providers>
            <LastVisitedProvider>
              {/* Remove the wrapper div */}
              <MainLayout>
                {/* <Theme> */}
                {children}
                {/* </Theme> */}
              </MainLayout>
              <CommandMenu />
            </LastVisitedProvider>
            {/* Footer rendered outside the growing div */}
            <Footer />
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  )
} 