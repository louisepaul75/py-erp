import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

// Initialize i18n for testing
const i18n = i18next.createInstance();

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
          'test.key': 'Test Value',
          'health.debugInfo': 'Debug Information',
          'health.environment': 'Environment',
          'health.version': 'Version',
          'health.databaseStatus': 'Database Status',
          'health.gitBranch': 'Git Branch',
          'health.apiAvailable': 'API Available',
          'common.yes': 'Yes',
          'common.no': 'No'
        },
      },
    },
    interpolation: {
      escapeValue: false,
    },
  });

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

interface AllProvidersProps {
  children: React.ReactNode;
}

const AllProviders = ({ children }: AllProvidersProps) => {
  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        {children}
      </I18nextProvider>
    </QueryClientProvider>
  );
};

const customRender = (ui: React.ReactElement, options = {}) =>
  render(ui, {
    wrapper: AllProviders,
    ...options,
  });

// re-export everything
export * from '@testing-library/react';

// override render method
export { customRender as render };

// Add a test to prevent "no tests" error
test.skip('empty test', () => {
  expect(true).toBe(true);
}); 