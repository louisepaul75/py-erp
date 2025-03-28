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
      {
        source: '/api/core/health',
        destination: 'http://localhost:8050/health/',
      },
      {
        source: '/api/core/git/branch',
        destination: 'http://localhost:8050/api/git/branch/',
      },
      {
        source: '/monitoring/:path*',
        destination: 'http://localhost:8050/monitoring/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8050/api/:path*',
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