'use client';

import { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';
import { csrfService } from '@/lib/auth/authService';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  }));

  // Initialize CSRF token on app load
  useEffect(() => {
    // Try to fetch and store a fresh CSRF token
    const initializeCsrf = async () => {
      try {
        await csrfService.fetchToken();
        console.log("CSRF token initialized on app load");
      } catch (error) {
        console.warn("Could not initialize CSRF token:", error);
      }
    };
    
    initializeCsrf();
  }, []);

  return (
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={queryClient}>
        {children}
        {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </I18nextProvider>
  );
} 