import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enable static exports for the app directory
  reactStrictMode: false,

  experimental: {
    ppr: true
  }
};

export default nextConfig;
