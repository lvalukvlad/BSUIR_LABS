/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    output: 'standalone',  // Важно для Docker
    swcMinify: true,
    images: {
      unoptimized: true,  // Для статического хостинга
    },
  }
  
  module.exports = nextConfig