// Build: v5.0.1 - Mobile navigation fix
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  // Enable experimental features for App Router
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['framer-motion', 'recharts', 'date-fns'],
  },
  // Image optimization
  images: {
    domains: [],
    formats: ['image/avif', 'image/webp'],
  },
  // Environment variables for client-side
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Rewrite API calls to backend
  // INTERNAL_API_URL is used for Docker networking (server-side)
  // NEXT_PUBLIC_API_URL is used for client-side browser requests
  async rewrites() {
    const internalApiUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${internalApiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
