'use client';

import { useTranslation } from 'react-i18next';

/**
 * Wrapper für react-i18next useTranslation mit standardmäßigem "common" Namespace
 * @param ns - Namespace oder Array von Namespaces (optional)
 * @returns useTranslation Objekt mit t, i18n, etc.
 */
export function useAppTranslation(ns: string | string[] = 'common') {
  return useTranslation(ns);
}

export default useAppTranslation; 