import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }: CardProps) {
  return (
    <h2 className={`text-2xl font-semibold text-gray-900 mb-4 ${className}`}>
      {children}
    </h2>
  )
}

export function CardContent({ children, className = '' }: CardProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {children}
    </div>
  )
}
