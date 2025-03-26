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
        // First check if we already have a token
        const existingToken = csrfService.getToken();
        if (existingToken) {
          console.log("Using existing CSRF token");
          return;
        }

        // If no token exists, try to fetch a new one
        const token = await csrfService.fetchToken();
        if (token) {
          console.log("CSRF token initialized on app load");
        } else {
          console.warn("Could not fetch CSRF token - will retry on next API call");
        }
      } catch (error) {
        console.warn("Error initializing CSRF token:", error);
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