'use client'

import { useState, useEffect, useCallback } from 'react'

type ProcessStep = {
  id: string
  name: string
  description: string
  percentageOfTotal: number
  status: 'waiting' | 'processing' | 'success' | 'error' | 'skipped' | 'initializing'
  details?: string
  startTime?: string
  endTime?: string
  error?: string
  isInitStep?: boolean
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
  const [connectionAttempts, setConnectionAttempts] = useState(0)
  const MAX_RECONNECT_ATTEMPTS = 3

  // Function to establish WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (connectionAttempts >= MAX_RECONNECT_ATTEMPTS) {
      setError('Maximum connection attempts reached. Please refresh the page to try again.')
      return
    }
    setConnectionAttempts(prev => prev + 1)
    if (!trackerId) {
      setError('No tracker ID provided')
      return
    }

    // Use relative URLs for API calls to leverage Next.js proxy
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/processing-status/${trackerId}`

    try {
      const newSocket = new WebSocket(wsUrl)

      newSocket.onopen = () => {
        setIsConnected(true)
        setError(null)
        setConnectionAttempts(0) // Reset counter on successful connection
      }

      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.error) {
            setError(data.error)
          } else {
            // Add initialization steps if they don't exist
            if (data.steps && !data.steps.some((s: ProcessStep) => s.isInitStep)) {
              const initSteps = [
                {
                  id: 'init-spacy',
                  name: 'Carregando SpaCy',
                  description: 'Loading spaCy model...',
                  percentageOfTotal: 0,
                  status: 'initializing',
                  isInitStep: true
                },
                {
                  id: 'init-keywords',
                  name: 'Inicializando Extratores',
                  description: 'Initializing keyword extractors...',
                  percentageOfTotal: 0,
                  status: 'waiting',
                  isInitStep: true
                },
                {
                  id: 'init-transformer',
                  name: 'Carregando Transformer',
                  description: 'Loading sentence transformer...',
                  percentageOfTotal: 0,
                  status: 'waiting',
                  isInitStep: true
                }
              ]

              // Update initialization steps based on backend logs
              const details = data.details as string | undefined
              if (details && initSteps.length >= 3) {
                // Destructure with type assertion since we checked length
                const [spacyStep, keywordsStep, transformerStep] = initSteps as [ProcessStep, ProcessStep, ProcessStep]
                
                if (details.includes('Loading spaCy model')) {
                  spacyStep.status = 'initializing'
                  keywordsStep.status = 'waiting'
                  transformerStep.status = 'waiting'
                } else if (details.includes('Initializing keyword extractors')) {
                  spacyStep.status = 'success'
                  keywordsStep.status = 'initializing'
                  transformerStep.status = 'waiting'
                } else if (details.includes('Loading sentence transformer')) {
                  spacyStep.status = 'success'
                  keywordsStep.status = 'success'
                  transformerStep.status = 'initializing'
                }
              }

              data.steps = [...initSteps, ...data.steps]
            }
            setStatus(data)
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err)
          setError('Failed to parse WebSocket message')
        }
      }

      newSocket.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
      }

      newSocket.onclose = () => {
        setIsConnected(false)
      }

      setSocket(newSocket)
    } catch (err) {
      console.error('WebSocket connection error:', err)
      setError(`Failed to connect: ${err instanceof Error ? err.message : String(err)}`)
    }
  }, [trackerId, connectionAttempts, MAX_RECONNECT_ATTEMPTS])

  // Connect when trackerId changes and cleanup on unmount
  useEffect(() => {
    if (!trackerId) return

    connectWebSocket()
    
    // Reconnect on network status change
    const handleOnline = () => {
      if (!isConnected && trackerId && connectionAttempts < MAX_RECONNECT_ATTEMPTS) {
        connectWebSocket()
      }
    }
    
    window.addEventListener('online', handleOnline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      if (socket) {
        socket.close()
        setSocket(null)
      }
    }
  }, [trackerId, connectWebSocket, isConnected, socket])

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
