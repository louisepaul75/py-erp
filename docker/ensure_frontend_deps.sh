#!/bin/bash

# Script to ensure frontend dependencies are properly installed
# This script is run after the container starts

cd /app/frontend-react

# Ensure required directories exist
mkdir -p src/lib src/hooks

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

# Ensure all dependencies are installed
echo "Ensuring all dependencies are installed..."
npm install --save-dev autoprefixer postcss tailwindcss

echo "Frontend dependencies setup complete!" 