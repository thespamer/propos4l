'use client'

import React, { createContext, useContext } from 'react'
import toast, { Toaster } from 'react-hot-toast'

interface ToastContextType {
  showToast: (message: string, type?: 'success' | 'error') => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    if (type === 'error') {
      toast.error(message)
    } else {
      toast.success(message)
    }
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <Toaster />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
