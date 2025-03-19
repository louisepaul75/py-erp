#!/bin/bash

# Script to ensure frontend dependencies are properly installed
# This script is run after the container starts

cd /app/frontend-react

# Ensure required directories exist
mkdir -p src/lib src/hooks src/__tests__/components src/__tests__/pages src/__tests__/hooks src/__tests__/utils

# Check if utils.ts exists, if not create it
if [ ! -f src/lib/utils.ts ]; then
  echo "Creating utils.ts..."
  cat > src/lib/utils.ts << 'EOL'
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines multiple class names using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
EOL
fi

# Check if use-mobile.ts exists, if not create it
if [ ! -f src/hooks/use-mobile.ts ]; then
  echo "Creating use-mobile.ts..."
  cat > src/hooks/use-mobile.ts << 'EOL'
import { useEffect, useState } from 'react';

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Function to check if the screen is mobile-sized
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    // Initial check
    checkMobile();

    // Add event listener for window resize
    window.addEventListener('resize', checkMobile);

    // Clean up event listener
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return isMobile;
}
EOL
fi

# Check if postcss.config.js exists, if not create it
if [ ! -f postcss.config.js ]; then
  echo "Creating postcss.config.js..."
  cat > postcss.config.js << 'EOL'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOL
fi

# Check if tailwind.config.js exists, if not create it
if [ ! -f tailwind.config.js ]; then
  echo "Creating tailwind.config.js..."
  cat > tailwind.config.js << 'EOL'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
EOL
fi

# Check if jsconfig.json exists, if not create it
if [ ! -f jsconfig.json ]; then
  echo "Creating jsconfig.json..."
  cat > jsconfig.json << 'EOL'
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
EOL
fi

# Update next.config.js to include experimental features
if ! grep -q "experimental" next.config.js; then
  echo "Updating next.config.js with experimental features..."
  sed -i 's/reactStrictMode: true,/reactStrictMode: true,\n  experimental: {\n    appDir: true,\n  },/' next.config.js
fi

# Update next.config.js to remove deprecated options
if grep -q "swcMinify" next.config.js; then
  echo "Updating next.config.js to remove deprecated options..."
  sed -i 's/swcMinify: true,//' next.config.js
fi

# Check if jest.config.js exists, if not create it
if [ ! -f jest.config.js ]; then
  echo "Creating jest.config.js..."
  cat > jest.config.js << 'EOL'
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
    '^.+\\.svg$': 'jest-transform-stub',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': 'jest-transform-stub',
  },
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/node_modules/**',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
EOL
fi

# Check if jest.setup.js exists, if not create it
if [ ! -f jest.setup.js ]; then
  echo "Creating jest.setup.js..."
  cat > jest.setup.js << 'EOL'
import '@testing-library/jest-dom';

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
  default: (props) => {
    // eslint-disable-next-line jsx-a11y/alt-text
    return <img {...props} />;
  },
}));
EOL
fi

# Check if .babelrc exists, if not create it
if [ ! -f .babelrc ]; then
  echo "Creating .babelrc..."
  cat > .babelrc << 'EOL'
{
  "presets": [
    "next/babel"
  ]
}
EOL
fi

# Check if test-utils.tsx exists, if not create it
if [ ! -f src/__tests__/utils/test-utils.tsx ]; then
  echo "Creating test-utils.tsx..."
  mkdir -p src/__tests__/utils
  cat > src/__tests__/utils/test-utils.tsx << 'EOL'
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
EOL
fi

# Create README for tests if it doesn't exist
if [ ! -f src/__tests__/README.md ]; then
  echo "Creating tests README.md..."
  cat > src/__tests__/README.md << 'EOL'
# React Frontend Testing Guide

This document provides an overview of the testing structure and conventions for the pyERP React frontend.

## Testing Structure

Our testing structure is organized as follows:

```
src/
└── __tests__/
    ├── components/       # Tests for React components
    ├── pages/            # Tests for Next.js pages
    ├── hooks/            # Tests for custom hooks
    └── utils/            # Test utilities and helpers
```

## Testing Libraries

We use the following testing libraries:

- **Jest**: As the test runner and assertion library
- **React Testing Library**: For rendering React components in tests
- **@testing-library/user-event**: For simulating user interactions
- **jest-dom**: For additional DOM testing assertions

## Running Tests

To run the tests, use the following npm scripts:

- `npm test`: Run all tests
- `npm run test:watch`: Run tests in watch mode (useful during development)
- `npm run test:coverage`: Run tests with coverage report
EOL
fi

# Ensure all dependencies are installed, including testing dependencies
echo "Ensuring all dependencies are installed..."
npm install --save-dev autoprefixer postcss tailwindcss

# Ensure testing dependencies are installed
echo "Ensuring testing dependencies are installed..."
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom @babel/preset-env @babel/preset-react @babel/preset-typescript jest-transform-stub identity-obj-proxy ts-jest

# Check if testing scripts are in package.json, if not add them
if ! grep -q "\"test\":" package.json; then
  echo "Adding test scripts to package.json..."
  sed -i 's/"lint": "next lint"/"lint": "next lint",\n    "test": "jest",\n    "test:watch": "jest --watch",\n    "test:coverage": "jest --coverage"/' package.json
fi

echo "Frontend dependencies and testing setup complete!" 