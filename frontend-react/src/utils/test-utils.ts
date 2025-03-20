/**
 * Test utilities for frontend tests
 */

/**
 * Mock window.matchMedia for components that use media queries
 * This is necessary for testing components that use media queries
 * like ResponsiveGridLayout which requires window.matchMedia
 */
export const mockMatchMedia = () => {
  window.matchMedia = jest.fn().mockImplementation((query) => {
    return {
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    };
  });
};

/**
 * Mock IntersectionObserver for components that use it
 * This is necessary for testing components that use IntersectionObserver
 */
export const mockIntersectionObserver = () => {
  const mockIntersectionObserver = jest.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  });
  window.IntersectionObserver = mockIntersectionObserver;
};

/**
 * Mock ResizeObserver for components that use it
 * This is necessary for testing components that use ResizeObserver
 */
export const mockResizeObserver = () => {
  window.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }));
};

/**
 * Setup all common browser API mocks at once
 */
export const setupBrowserMocks = () => {
  mockMatchMedia();
  mockIntersectionObserver();
  mockResizeObserver();
}; 