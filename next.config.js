/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['platform.magneto.com', 'graph.facebook.com', 'lh3.googleusercontent.com'],
  },
  // Enable experimental features if needed
  experimental: {
    // serverActions: true,
  },
}

module.exports = nextConfig
