'use client'

import { useState } from 'react'
import Link from 'next/link'
import { MobileMenu } from './mobile-menu'

export function Navigation() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <>
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center flex-1">
              {/* Mobile menu button */}
              <div className="flex items-center sm:hidden">
                <button
                  onClick={() => setIsMobileMenuOpen(true)}
                  className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
              <Link href="/" className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-blue-500">
                  Propos4l
                </span>
              </Link>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link 
                  href="/upload"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-indigo-600 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Upload
                </Link>
                <Link
                  href="/generate"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-indigo-600 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Gerar Proposta
                </Link>
                <Link
                  href="/history"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-indigo-600 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Histórico
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>
      <MobileMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />
    </>
  )
}
