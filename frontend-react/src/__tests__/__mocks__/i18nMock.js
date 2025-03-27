import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    common: {
      'login': 'Login',
      'error.invalidCredentials': 'Invalid credentials'
    }
  }
};

i18next
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    useSuspense: false,
    initImmediate: false,
    debug: true
  });

export const t = (key) => {
  return i18next.t(key);
};

export default i18next; 