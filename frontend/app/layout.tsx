import './globals.css'
import { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClientLayout } from './components/client-layout'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Propos4l - Automação Inteligente de Propostas',
  description: 'Sistema inteligente para automação e geração de propostas comerciais',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  )
}
