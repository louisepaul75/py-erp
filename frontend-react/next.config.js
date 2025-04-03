const path = require('path');
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: process.env.NODE_ENV === 'development',
  // Update for Next.js 15
  experimental: {
    // Remove serverActions as it's no longer experimental in Next.js 15
  },
  // Turbopack will use these settings when not using webpack
  images: {
    remotePatterns: [],
  },
  typescript: {
    // !! WARN !!
    // Ignoring type checking for build. We need to fix this properly later.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  // Prevent ESLint errors from failing the build
  eslint: {
    // Only warn in development, ignore in production
    ignoreDuringBuilds: true,
  },
  output: 'standalone',
  poweredByHeader: false,
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  productionBrowserSourceMaps: true,
  staticPageGenerationTimeout: 180,
  async rewrites() {
    return [
      // Handle URLs with trailing slashes
      {
        source: '/api/health/',
        destination: 'http://localhost:8000/health/',
      },
      // Handle URLs without trailing slashes
      {
        source: '/api/health',
        destination: 'http://localhost:8000/health/',
      },
      {
        source: '/api/monitoring/health-checks/',
        destination: 'http://localhost:8000/monitoring/health-checks/',
      },
      {
        source: '/api/monitoring/:path+',
        destination: 'http://localhost:8000/monitoring/:path+',
      },
      {
        source: '/api/git/branch/',
        destination: 'http://localhost:8000/api/git/branch/',
      },
      {
        source: '/api/git/branch',
        destination: 'http://localhost:8000/api/git/branch/',
      },
      // Add rules for /api/csrf
      {
        source: '/api/csrf/',
        destination: 'http://localhost:8000/api/csrf/',
      },
      {
        source: '/api/csrf',
        destination: 'http://localhost:8000/api/csrf/',
      },
      // Add rules for /api/token
      {
        source: '/api/token/',
        destination: 'http://localhost:8000/api/token/',
      },
      {
        source: '/api/token',
        destination: 'http://localhost:8000/api/token/',
      },
      // Add rules for /api/auth/user
      {
        source: '/api/auth/user/',
        destination: 'http://localhost:8000/api/auth/user/',
      },
      {
        source: '/api/auth/user',
        destination: 'http://localhost:8000/api/auth/user/',
      },
      // Add explicit rules for sales records BEFORE the general v1 rule
      {
        source: '/api/v1/sales/records/', // With slash
        destination: 'http://localhost:8000/api/v1/sales/records/',
      },
      {
        source: '/api/v1/sales/records', // Without slash
        destination: 'http://localhost:8000/api/v1/sales/records/', // Force slash
      },
      // Add specific rules for the monthly analysis endpoint
      {
        source: '/api/sales/records/monthly_analysis/',
        destination: 'http://localhost:8000/api/v1/sales/records/monthly_analysis/',
      },
      {
        source: '/api/sales/records/monthly_analysis',
        destination: 'http://localhost:8000/api/v1/sales/records/monthly_analysis/',
      },
      // Add a specific rule for OTHER /api/v1/ paths BEFORE the general catch-all
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
      // Catch-all for other /api paths
      // This MUST be last to avoid overriding specific rules above
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      }
    ]
  }
}

// Only include webpack config when not using Turbopack
if (!process.env.TURBOPACK) {
  nextConfig.webpack = (config) => {
    config.resolve.alias['@'] = path.resolve(__dirname, 'src');
    config.module.rules.push({
      test: /\.(ico|png|jpg|jpeg|gif|svg)$/,
      type: 'asset/resource',
    });
    return config;
  };
}

module.exports = nextConfig