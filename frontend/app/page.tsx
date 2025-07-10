import React from 'react'
import Link from 'next/link'
import { Card, CardTitle } from '@/components/ui/Card'

interface FeatureCardProps {
  title: string
  description: string
  href: string
  icon: React.ReactNode
  key?: string
}

function FeatureCard({ title, description, href, icon }: FeatureCardProps) {
  return (
    <Link href={href} className="group block">
      <Card className="h-full transform transition-all duration-200 hover:scale-105 hover:shadow-xl cursor-pointer">
        <div className="flex items-center mb-4">
          <div className="p-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors">
            {icon}
          </div>
        </div>
        <CardTitle>{title}</CardTitle>
        <p className="text-gray-600">{description}</p>
      </Card>
    </Link>
  )
}

export default function Home() {
  const features = [
    {
      title: 'Upload de Propostas',
      description: 'Faça upload de propostas existentes em PDF para enriquecer nossa base de conhecimento.',
      href: '/upload',
      icon: (
        <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      )
    },
    {
      title: 'Gerar Nova Proposta',
      description: 'Crie novas propostas personalizadas com base em parâmetros específicos.',
      href: '/generate',
      icon: (
        <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      )
    },
    {
      title: 'Histórico',
      description: 'Visualize e gerencie todas as propostas geradas anteriormente.',
      href: '/history',
      icon: (
        <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
  ]

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-extrabold text-gray-900 mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-blue-500">
            Propos4l
          </h1>
          <p className="text-2xl text-gray-600 max-w-2xl mx-auto">
            Automação Inteligente de Propostas Comerciais
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <FeatureCard key={feature.href} {...feature} />
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-600 max-w-2xl mx-auto">
            Utilize inteligência artificial para criar propostas personalizadas e profissionais em minutos.
            Aprenda com propostas anteriores e mantenha um histórico organizado.
          </p>
        </div>
      </div>
    </main>
  )
}
