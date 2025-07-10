'use client'

import { ToastProvider } from '../contexts/ToastContext'
import { LoadingProvider } from '../contexts/LoadingContext'
import { Navigation } from './navigation'

export function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <ToastProvider>
      <LoadingProvider>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</main>
        </div>
      </LoadingProvider>
    </ToastProvider>
  )
}
