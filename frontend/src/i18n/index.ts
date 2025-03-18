import { createI18n } from 'vue-i18n';
import en from './locales/en';
import de from './locales/de';
import cs from './locales/cs';

export const i18n = createI18n({
  legacy: false,
  locale: 'en',
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
