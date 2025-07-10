'use client'

import React, { createContext, useContext, useState } from 'react'

interface LoadingContextType {
  isLoading: boolean
  withLoading: <T>(promise: Promise<T>) => Promise<T>
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined)

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(false)

  const withLoading = async <T,>(promise: Promise<T>): Promise<T> => {
    setIsLoading(true)
    try {
      const result = await promise
      return result
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <LoadingContext.Provider value={{ isLoading, withLoading }}>
      {children}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary"></div>
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
