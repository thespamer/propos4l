'use client'

import { useState, useEffect, useCallback } from 'react'

type ProcessStep = {
  id: string
  name: string
  description: string
  percentageOfTotal: number
  status: 'waiting' | 'processing' | 'success' | 'error' | 'skipped'
  details?: string
  startTime?: string
  endTime?: string
  error?: string
}

type ProcessingStatus = {
  id: string
  fileName: string
  steps: ProcessStep[]
  currentStepId: string | null
  overallProgress: number
  startTime: string
  endTime?: string
  isComplete: boolean
}

type UseProcessingStatusResult = {
  status: ProcessingStatus | null
  error: string | null
  isConnected: boolean
}

export function useProcessingStatus(trackerId: string | null): UseProcessingStatusResult {
  const [status, setStatus] = useState<ProcessingStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [socket, setSocket] = useState<WebSocket | null>(null)

  // Function to establish WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!trackerId) {
      setError('No tracker ID provided')
      return
    }

    // Close existing connection if any
    if (socket) {
      socket.close()
    }

    try {
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/ws/processing-status/${trackerId}`

      const newSocket = new WebSocket(wsUrl)

      newSocket.onopen = () => {
        setIsConnected(true)
        setError(null)
      }

      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.error) {
            setError(data.error)
          } else {
            setStatus(data)
          }
        } catch (err) {
          setError('Failed to parse WebSocket message')
          console.error('WebSocket message parse error:', err)
        }
      }

      newSocket.onerror = (event) => {
        setError('WebSocket connection error')
        setIsConnected(false)
        console.error('WebSocket error:', event)
      }

      newSocket.onclose = () => {
        setIsConnected(false)
      }

      setSocket(newSocket)

      // Cleanup function
      return () => {
        newSocket.close()
        setSocket(null)
        setIsConnected(false)
      }
    } catch (err) {
      setError(`Failed to connect: ${err instanceof Error ? err.message : String(err)}`)
      setIsConnected(false)
    }
  }, [trackerId, socket])

  // Connect when trackerId changes
  useEffect(() => {
    const cleanup = connectWebSocket()
    
    // Reconnect on network status change
    const handleOnline = () => {
      if (!isConnected && trackerId) {
        connectWebSocket()
      }
    }
    
    window.addEventListener('online', handleOnline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      if (cleanup) cleanup()
    }
  }, [trackerId, connectWebSocket, isConnected])

  // Fetch initial status via REST API if WebSocket fails
  useEffect(() => {
    if (!trackerId || isConnected || !navigator.onLine) return

    const fetchStatus = async () => {
      try {
        const response = await fetch(`/api/processing-status/${trackerId}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setStatus(data)
      } catch (err) {
        console.error('Failed to fetch status:', err)
        // Don't set error here as it might be temporary and WebSocket might still connect
      }
    }

    // Try REST API as fallback
    fetchStatus()
  }, [trackerId, isConnected])

  return { status, error, isConnected }
}
