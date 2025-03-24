/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: process.env.NODE_ENV === 'development',
  experimental: {
    // appDir is now the default in Next.js 14+
  },
  // Add this to disable favicon requests
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(ico|png|jpg|jpeg|gif|svg)$/,
      type: 'asset/resource',
    });
    return config;
  },
  // Add output configuration to ensure static files are generated correctly
  output: 'standalone',
  poweredByHeader: false,
  // Configure the build to handle dynamic routes properly
  distDir: '.next',
  // Don't attempt to optimize pages that aren't being correctly detected
  optimizeFonts: true,
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  // Disable minification for easier debugging
  swcMinify: false,
  productionBrowserSourceMaps: true,
  // Increase timeout for builds
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

module.exports = nextConfig 