import React from 'react';
import { render, RenderOptions } from '@testing-library/react';

// Simple wrapper that doesn't need i18n
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      {children}
    </>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// re-export everything
export * from '@testing-library/react';

// override render method
export { customRender as render };

// Add a simple test to prevent "no tests" errors
test('true is true', () => {
  expect(true).toBe(true);
});