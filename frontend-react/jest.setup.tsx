import '@testing-library/jest-dom';
import * as React from 'react';
import fetchMock from 'jest-fetch-mock';

// Enable fetch mocks globally
fetchMock.enableMocks();

// Add polyfills for TextEncoder and TextDecoder
// This is needed for JSDOM in some tests
if (typeof global.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}

// Initialize jest-fuzz if needed
try {
  const jestFuzz = require('jest-fuzz');
  // Add any additional jest-fuzz configuration here if needed
} catch (error) {
  console.warn('jest-fuzz not available:', error.message);
}

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
    events: {
      on: jest.fn(),
      off: jest.fn(),
      emit: jest.fn(),
    },
  }),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn()
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  redirect: jest.fn()
}));

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: function MockImage(props) {
    return React.createElement('img', { ...props });
  },
}));

// Mock i18next
const mockI18n = {
  use: function() { return this; },
  init: () => Promise.resolve(),
  t: (key: string) => key,
  language: 'en',
  changeLanguage: jest.fn(),
};

jest.mock('i18next', () => mockI18n);

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: mockI18n,
  }),
  initReactI18next: {
    type: '3rdParty',
    init: () => {},
  },
}));

jest.mock('i18next-browser-languagedetector', () => ({
  type: '3rdParty',
  init: () => {},
}));

jest.mock('i18next-http-backend', () => ({
  type: '3rdParty',
  init: () => {},
})); 