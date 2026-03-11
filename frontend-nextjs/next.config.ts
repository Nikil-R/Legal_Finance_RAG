import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Disable image optimization for deployment flexibility
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
