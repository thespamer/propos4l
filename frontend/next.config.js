/** @type {import('next').NextConfig} */

const nextConfig = {
  // Proxy configuration for backend API
  async rewrites() {
    // Determine backend URL based on environment
    const isDocker = process.env.DOCKER_CONTAINER === 'true'
    const backendUrl = isDocker
      ? (process.env.BACKEND_URL || 'http://backend:8000')
      : (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000')

    // Log environment configuration for debugging
    console.log('Next.js Proxy Configuration:', {
      isDocker,
      backendUrl,
      BACKEND_URL: process.env.BACKEND_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      DOCKER_CONTAINER: process.env.DOCKER_CONTAINER
    })

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/ws/:path*',
        destination: `${backendUrl}/ws/:path*`,
      },
    ]
  },
  reactStrictMode: true,
  output: 'standalone',
  poweredByHeader: false,
  compress: true,

  // Enable source maps in development
  productionBrowserSourceMaps: process.env.NODE_ENV === 'development',

  // Strict type checking
  typescript: {
    // We want type errors to fail the build in production
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },

  // ESLint during builds
  eslint: {
    // We want linting errors to fail the build in production
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },

  // Configure webpack
  webpack: (config, { dev, isServer }) => {
    // Alias configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': '.',
      '@components': './components',
      '@contexts': './contexts',
      '@hooks': './hooks',
      '@lib': './lib',
      '@styles': './styles',
      '@utils': './utils',
    }

    // Optimization settings
    if (!dev && !isServer) {
      // Enable tree shaking and minification
      config.optimization.minimize = true
      config.optimization.usedExports = true

      // Split chunks optimization
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          defaultVendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            reuseExistingChunk: true,
          },
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
        },
      }
    }

    return config
  },

  // Headers configuration
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
