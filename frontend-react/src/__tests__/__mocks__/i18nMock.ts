import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Initialize i18n for tests
i18n
  .use(initReactI18next)
  .init({
    lng: 'en',
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    resources: {
      en: {
        common: {
          login: 'Login',
          logout: 'Logout',
          profile: 'Profile',
          error: {
            invalidCredentials: 'Invalid credentials',
            networkError: 'Network error',
          }
        }
      }
    },
    interpolation: {
      escapeValue: false, // React already escapes values
    }
  });

// Add a test to ensure i18n is working
describe('i18n mock', () => {
  it('should translate text', () => {
    expect(i18n.t('common:login')).toBe('Login');
    expect(i18n.t('common:error.invalidCredentials')).toBe('Invalid credentials');
  });
});

export default i18n; 