import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider, initReactI18next } from 'react-i18next';
import i18next from 'i18next';

// Create a new QueryClient instance for testing
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Initialize i18next for testing
i18next
  .use(initReactI18next)
  .init({
    lng: 'en',
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: {
        common: {
          test: 'test',
          'navigation.home': 'Home',
          'navigation.products': 'Products',
          'navigation.sales': 'Sales',
          'navigation.production': 'Production',
          'navigation.inventory': 'Inventory',
          'navigation.settings': 'Settings'
        }
      }
    },
    react: {
      useSuspense: false
    },
    initImmediate: false
  });

// Create a wrapper component that provides both react-query and i18n context
const AllProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18next}>
        {children}
      </I18nextProvider>
    </QueryClientProvider>
  );
};

// Create a custom render function that wraps the component with the providers
const customRender = (ui: React.ReactElement) => {
  return render(ui, { wrapper: AllProviders });
};

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Add a simple test to prevent "no tests" errors
test('true is true', () => {
  expect(true).toBe(true);
});