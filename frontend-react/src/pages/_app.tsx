import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../lib/query/queryClient';
import { useEffect } from 'react';

// Global error handler to patch textContent null error
function patchDOMTextContentIssue() {
  if (typeof window !== 'undefined') {
    // Save the original Object.defineProperty
    const originalDefineProperty = Object.defineProperty;
    
    // Create a patched version of textContent getter
    const createSafeTextContentGetter = (originalGetter: () => string | null) => {
      return function(this: any) {
        try {
          const result = originalGetter.call(this);
          return result;
        } catch (e) {
          console.warn('Caught textContent error:', e);
          return '';
        }
      };
    };
    
    // Override the defineProperty method to intercept textContent property definitions
    Object.defineProperty = function(obj, prop, descriptor) {
      if (prop === 'textContent' && descriptor && descriptor.get) {
        descriptor.get = createSafeTextContentGetter(descriptor.get);
      }
      return originalDefineProperty(obj, prop, descriptor);
    };
    
    // Add a global error handler for uncaught errors
    window.addEventListener('error', (event) => {
      if (event.message.includes('textContent') && event.message.includes('null')) {
        console.warn('Caught textContent error in global handler:', event);
        event.preventDefault();
        event.stopPropagation();
        return true;
      }
    }, true);
  }
}

export default function App({ Component, pageProps }: AppProps) {
  // Apply the DOM patch when the app loads
  useEffect(() => {
    patchDOMTextContentIssue();
  }, []);
  
  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
} 