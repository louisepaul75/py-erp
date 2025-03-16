/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
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
  async rewrites() {
    return [
      {
        source: '/core/health',
        destination: 'http://localhost:8050/health/',
      },
      {
        source: '/core/git/branch',
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