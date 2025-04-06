'use client';

import { useTranslation, UseTranslationOptions } from 'react-i18next';
import { useState, useEffect } from 'react';
import { resources } from '@/lib/i18n';

type ResourceType = typeof resources;
type LanguageKeys = keyof ResourceType;
type NamespaceKeys<T extends LanguageKeys> = keyof ResourceType[T];
type TranslationKeys<T extends LanguageKeys, N extends NamespaceKeys<T>> = keyof ResourceType[T][N];

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
    return key;
  };

  // If we're in a test environment, always use the translation function
  const isTest = process.env.NODE_ENV === 'test';

  // Use translation.ready which indicates if requested namespaces are loaded.
  // Also ensure we are on the client and the initial mount effect has run (loaded).
  const shouldUseRealT = isTest || (isClient && loaded && translation.ready);

  return {
    ...translation,
    // Use the real 't' function if ready, otherwise the fallback
    t: shouldUseRealT ? translation.t : serverSideFallback,
    // Expose the underlying ready state
    ready: translation.ready,
  };
}

export default useAppTranslation; 