import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Check if we're running on the client side
const isClient = typeof window !== 'undefined';

// Define static resources for the 'common' namespace to avoid initial loading delay
export const resources = {
  de: {
    common: {
      'navigation.home': 'Home',
      'navigation.products': 'Produkte',
      'navigation.sales': 'Verkauf',
      'navigation.production': 'Produktion',
      'navigation.inventory': 'Inventar',
      'navigation.settings': 'Einstellungen'
    }
  },
  en: {
    common: {
      'navigation.home': 'Home',
      'navigation.products': 'Products',
      'navigation.sales': 'Sales',
      'navigation.production': 'Production',
      'navigation.inventory': 'Inventory',
      'navigation.settings': 'Settings'
    }
  }
};

// Don't initialize i18next on the server
if (isClient) {
  i18n
    // load translations using http (default public/locales)
    .use(Backend)
    // detect user language
    .use(LanguageDetector)
    // pass the i18n instance to react-i18next
    .use(initReactI18next)
    // init i18next
    .init({
      fallbackLng: 'de', // default language
      supportedLngs: ['de', 'en', 'fr', 'es'],
      debug: process.env.NODE_ENV === 'development',
      
      interpolation: {
        escapeValue: false, // not needed for react as it escapes by default
      },
      
      // react-specific options
      react: {
        useSuspense: false, // prevents issues with SSR
      },
      
      // load translation resources from
      backend: {
        loadPath: '/locales/{{lng}}/{{ns}}.json',
      },
      
      // Provide static resources for immediate use
      resources,
      
      defaultNS: 'common',
      ns: ['common', 'auth', 'products', 'dashboard'],
      
      // Initialize with resources to prevent loading delays
      preload: ['de', 'en'],
    });
}

export default i18n; 