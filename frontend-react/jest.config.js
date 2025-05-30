/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jsdom',
  testMatch: ['**/__tests__/**/*.test.[jt]s?(x)'],
  setupFiles: ['<rootDir>/dotenv.setup.js'],
  modulePaths: ['<rootDir>/src'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.tsx'],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/__mocks__/',
    '/.next/',
    '<rootDir>/src/__tests__/setup/mockWindowSetup.js',
    '<rootDir>/src/__tests__/components/LanguageSelector.mock.tsx',
    '<rootDir>/src/__tests__/utils/fuzz-utils.ts'
  ],
  transform: {
    '^.+\\.[tj]sx?$': ['babel-jest', { configFile: './babel.config.js' }],
  },
  transformIgnorePatterns: [
    '/node_modules/(?!jest-fuzz|ky/)',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageProvider: 'v8',
  coverageReporters: ['json', 'lcov', 'clover', 'text', 'text-summary'],
};

module.exports = config; 