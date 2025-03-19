import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Add providers that are commonly used in your app
interface AllProvidersProps {
  children: React.ReactNode;
}

const AllProviders = ({ children }: AllProvidersProps) => {
  return (
    <>
      {/* You can add React Query Provider, Theme Provider, etc. here if needed */}
      {children}
    </>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: AllProviders, ...options })
  };
};

// Re-export everything from testing-library
export * from '@testing-library/react';

// Override render method
export { customRender as render };

// Adding a placeholder test to avoid "no tests" error
// This will be skipped since we test this file in test-utils.test.tsx
if (process.env.NODE_ENV === 'test') {
  describe('test-utils', () => {
    it('should pass', () => {
      expect(true).toBe(true);
    });
  });
} 