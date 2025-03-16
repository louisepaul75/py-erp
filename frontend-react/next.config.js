/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
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