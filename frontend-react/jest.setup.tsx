require('whatwg-fetch');
require('@testing-library/jest-dom');
const React = require('react');
const fetchMock = require('jest-fetch-mock');
const i18n = require('i18next');
const { initReactI18next } = require('react-i18next');

// Load environment variables from .env file at the project root
// <rootDir> in Jest config points to frontend-react, so ../ points to the workspace root
// dotenv.config({ path: path.resolve(__dirname, '../.env') }); 
// ^^^ Moved to dotenv.setup.js and executed via setupFiles in jest.config.js

// Explicitly set API_URL for tests if it's defined after dotenv load
process.env.API_URL = process.env.API_URL || 'http://localhost:8000'; // Provide a default if not set

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
    // Require React inside the factory function
    const React = require('react'); 
    return React.createElement('img', { ...props });
  },
}));

// Mock i18next
// Configure i18n instance before mocking it
i18n
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: { translation: {} },
      de: { translation: {} },
    },
  });

// Use jest.doMock which is not hoisted
jest.doMock('i18next', () => ({
  // Define only the necessary mock functions inline
  changeLanguage: jest.fn((lng) => Promise.resolve()),
  // Ensure t always returns the key for consistent mocking
  t: (key: string) => key,
}));

// Use jest.doMock which is not hoisted
jest.doMock('react-i18next', () => ({
  useTranslation: () => ({
    // Ensure t always returns the key
    t: (key: string) => key,
    // Define the nested i18n mock object inline without spreading
    i18n: {
      changeLanguage: jest.fn((lng) => Promise.resolve()),
      // Ensure nested t always returns the key
      t: (key: string) => key,
    },
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