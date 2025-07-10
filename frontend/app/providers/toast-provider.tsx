'use client'

import { ReactNode } from 'react'
import { Toaster } from 'react-hot-toast'

export function ToastProvider({ children }: { children: ReactNode }) {
  return (
    <>
      <Toaster position="top-right" />
      {children}
    </>
  )
}
