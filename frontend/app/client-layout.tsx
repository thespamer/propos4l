'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ToastProvider } from '../contexts/ToastContext'
import { LoadingProvider } from '../contexts/LoadingContext'
import { MobileMenu } from '../components/ui/MobileMenu'

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <LoadingProvider>
      <ToastProvider>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation */}
          <nav className="bg-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                {/* Logo and Desktop Navigation */}
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <Link href="/" className="text-xl font-bold text-gray-800">
                      Propos4l
                    </Link>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                    <Link href="/" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">
                      Home
                    </Link>
                    <Link href="/generate" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">
                      Gerar Proposta
                    </Link>
                    <Link href="/history" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">
                      Histórico
                    </Link>
                  </div>
                </div>

                {/* Mobile menu button */}
                <div className="sm:hidden flex items-center">
                  <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                  >
                    <span className="sr-only">Open main menu</span>
                    {!isMobileMenuOpen ? (
                      <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                      </svg>
                    ) : (
                      <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Mobile menu */}
            <MobileMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />
          </nav>

          {/* Main content */}
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
      </ToastProvider>
    </LoadingProvider>
  )
}
