import React, { useState } from 'react'
import Link from 'next/link'

interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  return (
    <div
      className={`fixed inset-0 z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black bg-opacity-50 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
      />

      {/* Menu content */}
      <div className="absolute right-0 h-full w-64 bg-white shadow-xl">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-blue-500">
              Menu
            </span>
            <button
              onClick={onClose}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          <Link
            href="/upload"
            className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
            onClick={onClose}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Upload
          </Link>

          <Link
            href="/generate"
            className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
            onClick={onClose}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Gerar Proposta
          </Link>

          <Link
            href="/history"
            className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
            onClick={onClose}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Histórico
          </Link>
        </nav>
      </div>
    </div>
  )
}
