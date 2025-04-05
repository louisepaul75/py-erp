module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    // Handle CSS imports (e.g., .css, .scss, .less)
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    // Handle module aliases - Corrected $1 placement
    '^@/(.*)$': '<rootDir>/frontend-react/src/$1',
  },
  // Use the setup file (now with .ts extension)
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  // Transform specific node_modules that use ES Modules
  transformIgnorePatterns: [
    // Allow transforming ky and other necessary es-modules
    '/node_modules/(?!ky)/' 
  ],
}; 