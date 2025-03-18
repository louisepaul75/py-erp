// Vue I18n configuration
import { createI18n } from 'vue-i18n';

// Import language files
import en from '../i18n/locales/en';
import de from '../i18n/locales/de';
import cs from '../i18n/locales/cs';

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'de', // set default locale to German
  fallbackLocale: 'en',
  messages: {
    en,
    de,
    cs
  },
  globalInjection: true,
  silentTranslationWarn: true,
  silentFallbackWarn: true
});

export default i18n;
