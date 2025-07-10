import React, { createContext, useContext, useState, useCallback } from 'react'

interface LoadingContextType {
  isLoading: boolean
  setLoading: (loading: boolean) => void
  withLoading: <T>(promise: Promise<T>) => Promise<T>
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined)

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(false)

  const withLoading = useCallback(async <T,>(promise: Promise<T>): Promise<T> => {
    try {
      setIsLoading(true)
      const result = await promise
      return result
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <LoadingContext.Provider value={{ isLoading, setLoading: setIsLoading, withLoading }}>
      {children}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="mt-4 text-gray-700">Carregando...</p>
          </div>
        </div>
      )}
    </LoadingContext.Provider>
  )
}

export function useLoading() {
  const context = useContext(LoadingContext)
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider')
  }
  return context
}
