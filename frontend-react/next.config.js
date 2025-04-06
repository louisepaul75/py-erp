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
      // Health check routes
      {
        source: '/health/',
        destination: 'http://localhost:8000/api/health/',
      },
      {
        source: '/health',
        destination: 'http://localhost:8000/api/health/',
      },
      // Direct v1 routes - specific routes first
      {
        // Match /v1/monitoring/health-checks optionally followed by a slash
        source: '/v1/monitoring/health-checks{/}?',
        destination: 'http://localhost:8000/api/v1/monitoring/health-checks/',
      },
      {
        // Match /v1/git/branch optionally followed by a slash
        source: '/v1/git/branch{/}?',
        destination: 'http://localhost:8000/api/v1/git/branch/',
      },
      {
        source: '/v1/dashboard/summary/',
        destination: 'http://localhost:8000/api/v1/dashboard/summary/',
      },
      // Sales analysis routes with query parameters
      {
        source: '/v1/sales/records/monthly_analysis',
        destination: 'http://localhost:8000/api/v1/sales/records/monthly_analysis',
      },
      {
        source: '/v1/sales/records/annual_analysis',
        destination: 'http://localhost:8000/api/v1/sales/records/annual_analysis',
      },
      // Regular sales routes
      {
        source: '/v1/sales/records/',
        destination: 'http://localhost:8000/api/v1/sales/records/',
      },
      {
        source: '/v1/sales/records/:id/items/',
        destination: 'http://localhost:8000/api/v1/sales/records/:id/items/',
      },
      {
        source: '/v1/inventory/storage-locations/',
        destination: 'http://localhost:8000/api/v1/inventory/storage-locations/',
      },
      {
        source: '/v1/inventory/bin-locations/by-order/:id/',
        destination: 'http://localhost:8000/api/v1/inventory/bin-locations/by-order/:id/',
      },
      // Wildcard for any other v1 routes (MUST be after specific routes)
      {
        source: '/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
      // Authentication routes
      {
        source: '/csrf/',
        destination: 'http://localhost:8000/api/csrf/',
      },
      {
        source: '/csrf',
        destination: 'http://localhost:8000/api/csrf/',
      },
      {
        source: '/token/',
        destination: 'http://localhost:8000/api/token/',
      },
      {
        source: '/token',
        destination: 'http://localhost:8000/api/token/',
      },
      {
        source: '/auth/user/',
        destination: 'http://localhost:8000/api/auth/user/',
      },
      {
        source: '/auth/user',
        destination: 'http://localhost:8000/api/auth/user/',
      },
      // Sales API paths (non-versioned)
      {
        source: '/sales/records/',
        destination: 'http://localhost:8000/api/sales/records/',
      },
      {
        source: '/sales/records/monthly_analysis/',
        destination: 'http://localhost:8000/api/sales/records/monthly_analysis/',
      },
      {
        source: '/sales/records/annual_analysis/',
        destination: 'http://localhost:8000/api/sales/records/annual_analysis/',
      },
      // Dashboard endpoints
      {
        source: '/dashboard/summary/',
        destination: 'http://localhost:8000/api/dashboard/summary/',
      },
      {
        source: '/dashboard/config/',
        destination: 'http://localhost:8000/api/dashboard/config/',
      },
      // Catch-all for all other paths - add /api prefix
      {
        source: '/:path*',
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