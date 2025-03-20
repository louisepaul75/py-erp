'use client';

import { useTranslation, UseTranslationOptions } from 'react-i18next';
import { useState, useEffect } from 'react';
import { resources } from '@/lib/i18n';

/**
 * Wrapper for react-i18next useTranslation with default "common" namespace
 * @param ns - Namespace or array of namespaces (optional)
 * @returns useTranslation object with t, i18n, etc.
 */
export function useAppTranslation(ns: string | readonly string[] = 'common') {
  const [loaded, setLoaded] = useState(false);
  const isClient = typeof window !== 'undefined';
  
  // Cast the namespace to any to avoid TypeScript errors
  // This is safe because we're using string namespaces like 'common', 'auth', etc.
  const translation = useTranslation(ns as any, {
    useSuspense: false,
  });

  // Ensure the component doesn't throw during SSR
  useEffect(() => {
    setLoaded(true);
  }, []);

  // Server-side translation function that uses our fallbacks
  const serverSideFallback = (key: string) => {
    // For keys like 'navigation.home' in the 'common' namespace
    const mainNs = Array.isArray(ns) ? ns[0] : ns;
    const lang = 'en'; // Default to English for SSR and tests
    
    if (resources[lang] && resources[lang][mainNs] && resources[lang][mainNs][key]) {
      return resources[lang][mainNs][key];
    }
    
    // Fallback to the key itself if no translation is found
    return key;
  };

  // If we're in a test environment, always use the translation function
  const isTest = process.env.NODE_ENV === 'test';

  return {
    ...translation,
    t: (isTest || (isClient && loaded && translation.i18n?.isInitialized)) ? translation.t : serverSideFallback,
    ready: isClient ? translation.ready : true,
  };
}

export default useAppTranslation; 