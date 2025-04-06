import { TextEncoder, TextDecoder } from 'util';

// Polyfill TextEncoder/TextDecoder for jsdom
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as typeof global.TextDecoder; // Need type assertion

// Import the jest-dom matchers
import '@testing-library/jest-dom';

// Mock the Next.js router (both old and new)
import mockRouter from 'next-router-mock';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';

jest.mock('next/router', () => require('next-router-mock'));
jest.mock('next/navigation', () => require('next-router-mock'));

// Optional: Add any other global setup here, e.g., mocking fetch 