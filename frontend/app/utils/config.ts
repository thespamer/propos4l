/**
 * Configuration utilities for backend API URLs
 */

/**
 * Determina se o código está sendo executado no servidor (SSR) ou no cliente (browser)
 */
export function isServer(): boolean {
  return typeof window === 'undefined'
}

/**
 * Determina se o código está sendo executado dentro de um container Docker
 */
export function isDockerContainer(): boolean {
  return process.env.DOCKER_CONTAINER === 'true'
}

/**
 * Retorna a URL base do backend com base no ambiente de execução:
 * - Em SSR + Docker: usa BACKEND_URL ou http://backend:8000
 * - Em SSR local: usa NEXT_PUBLIC_API_URL ou http://127.0.0.1:8000
 * - No browser: usa NEXT_PUBLIC_API_URL ou window.location.origin
 */
export function getBackendUrl(): string {
  // Se estiver rodando em SSR
  if (isServer()) {
    // Se estiver em um container Docker
    if (isDockerContainer()) {
      return process.env.BACKEND_URL || 'http://backend:8000'
    }
    // Se estiver rodando localmente
    return process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  }

  // Se estiver no browser
  return process.env.NEXT_PUBLIC_API_URL || `${window.location.protocol}//${window.location.host}`
}

/**
 * Get WebSocket URL for real-time updates
 */
export function getWebSocketUrl(path: string): string {
  if (typeof window === 'undefined') {
    return '' // WebSocket connections are only made client-side
  }

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${wsProtocol}//${window.location.host}${path}`
}
