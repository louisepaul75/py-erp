import './globals.css'
import type { Metadata } from 'next'
import { Footer } from '@/components/Footer'
import { Providers } from './providers'
import MainLayout from '@/components/layout/MainLayout'
// import { Theme } from '@radix-ui/themes';

export const metadata: Metadata = {
  title: 'pyERP - Enterprise Resource Planning',
  description: 'Modern ERP system built with Python and React',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
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
        {/* Add script to set theme before rendering to prevent flash */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const savedTheme = localStorage.getItem('theme');
                  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                  const theme = savedTheme || systemTheme;
                  
                  if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {
                  console.error('Error setting initial theme:', e);
                }
              })();
            `,
          }}
        />
        {/* Add empty CSRF token meta tag that can be populated by API responses */}
        <meta name="csrf-token" content="" />
      </head>
      <body className="min-h-screen bg-gray-50 dark:bg-gray-900 text-amber-950 dark:text-gray-100">
        <Providers>
          <MainLayout>
            {/* <Theme> */}
            {children}
            {/* </Theme> */}
          </MainLayout>
          <Footer />
        </Providers>
      </body>
    </html>
  )
} 