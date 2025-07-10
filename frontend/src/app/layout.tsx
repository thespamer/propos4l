import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

import './globals.css'

export const metadata: Metadata = {
  title: 'Propos4l - AI-Powered Proposal Automation',
  description: 'Generate and manage professional proposals with AI assistance',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {children}
        </div>
      </body>
    </html>
  )
}
