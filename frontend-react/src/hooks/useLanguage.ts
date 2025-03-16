'use client';

import { useState, useEffect } from 'react';

type Language = 'en' | 'de' | 'fr' | 'es';

export function useLanguage() {
  const [language, setLanguage] = useState<Language>('en');
  
  // Initialize language from localStorage or browser preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language | null;
    const browserLanguage = navigator.language.split('-')[0] as Language;
    
    if (savedLanguage) {
      setLanguage(savedLanguage);
    } else if (['en', 'de', 'fr', 'es'].includes(browserLanguage)) {
      setLanguage(browserLanguage);
    }
  }, []);
  
  // Update localStorage when language changes
  useEffect(() => {
    localStorage.setItem('language', language);
    // Here you would also update the HTML lang attribute
    document.documentElement.lang = language;
  }, [language]);
  
  // Change language function
  const changeLanguage = (newLanguage: Language) => {
    setLanguage(newLanguage);
  };
  
  return { language, changeLanguage };
}

export default useLanguage; 