import '@testing-library/jest-dom';
import React from 'react';

// Initialize jest-fuzz if needed
try {
  const jestFuzz = require('jest-fuzz');
  // Add any additional jest-fuzz configuration here if needed
} catch (error: any) {
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

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: function MockImage(props: any) {
    return <img {...props} />;
  },
}));

// Mock ky
jest.mock('ky', () => {
  interface MockKy {
    extend: jest.Mock;
    post: jest.Mock;
    get: jest.Mock;
    put: jest.Mock;
    delete: jest.Mock;
    create: jest.Mock;
  }

  const mockKy: MockKy = {
    extend: jest.fn(),
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    create: jest.fn(() => mockKy),
  };
  return {
    __esModule: true,
    default: mockKy,
  };
});

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ status: 'ok', branch: 'main' }),
  })
) as jest.Mock;

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