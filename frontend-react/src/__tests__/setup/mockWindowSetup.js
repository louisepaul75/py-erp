/**
 * @jest-environment jsdom
 * @jest-environment-options {"html": "<html><body></body></html>"}
 * @jest-skip - This is a setup file for Jest, not a test suite
 * 
 * This file is a setup file for Jest and not a test suite.
 * It provides global mocks for window related objects and functions.
 */

// Mock window properties that aren't available in Jest's JSDOM
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() { return null; }
  unobserve() { return null; }
  disconnect() { return null; }
};

// Set up window.innerWidth/Height for responsive tests
window.innerWidth = 1200; // Default to desktop
window.innerHeight = 800;

// Create a helper function to resize window that can be imported in tests
global.resizeWindow = (width, height) => {
  window.innerWidth = width;
  window.innerHeight = height;
  window.dispatchEvent(new Event('resize'));
};

// Mock getComputedStyle
window.getComputedStyle = jest.fn().mockImplementation(element => {
  return {
    display: 'block',
    visibility: 'visible',
    getPropertyValue: jest.fn(prop => {
      if (prop === 'display') return 'block';
      if (prop === 'visibility') return 'visible';
      return '';
    }),
  };
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}

window.IntersectionObserver = MockIntersectionObserver;

// Mock ResizeObserver
window.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
})); 